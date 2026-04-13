import re
from django.utils import timezone
from datetime import timedelta
from .models import Hospital, Domain, Plan, Subscription


def slugify_schema(name: str) -> str:
    """Convert hospital name to a valid PostgreSQL schema name."""
    slug = re.sub(r"[^\w]", "_", name.lower())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return f"hospital_{slug}"


def provision_hospital(
    name: str,
    email: str,
    subdomain: str,
    plan_tier: str = Plan.Tier.BASIC,
    base_domain: str = "yoursaas.com",
    trial_days: int = 14,
) -> Hospital:
    """
    Create a new tenant hospital with:
      - its own PostgreSQL schema
      - a primary domain
      - a trial subscription on the chosen plan

    Call this from your signup view or a Celery task.
    """
    schema_name = slugify_schema(name)

    hospital = Hospital(
        schema_name=schema_name,
        name=name,
        email=email,
        on_trial=True,
        trial_ends_on=(timezone.now() + timedelta(days=trial_days)).date(),
    )
    # save() triggers django-tenants to CREATE SCHEMA in PostgreSQL
    hospital.save()

    Domain.objects.create(
        domain=f"{subdomain}.{base_domain}",
        tenant=hospital,
        is_primary=True,
    )

    plan = Plan.objects.get(tier=plan_tier)
    Subscription.objects.create(
        hospital=hospital,
        plan=plan,
        status=Subscription.Status.TRIALING,
    )

    return hospital
