import pytest
from apps.tenants.models import Plan, Hospital, Subscription
from apps.tenants.services import provision_hospital, slugify_schema


@pytest.fixture
def basic_plan(db):
    return Plan.objects.create(
        name="Basic",
        tier=Plan.Tier.BASIC,
        price_monthly=99,
        max_users=10,
        max_patients=500,
    )


def test_slugify_schema():
    assert slugify_schema("Nairobi General Hospital") == "hospital_nairobi_general_hospital"
    assert slugify_schema("St. Mary's") == "hospital_st_mary_s"


@pytest.mark.django_db
def test_provision_hospital_creates_schema(basic_plan):
    hospital = provision_hospital(
        name="Test Hospital",
        email="admin@test.hospital",
        subdomain="test",
        base_domain="localhost",
    )
    assert Hospital.objects.filter(schema_name="hospital_test_hospital").exists()
    assert hospital.subscription.status == Subscription.Status.TRIALING
    assert hospital.domains.filter(domain="test.localhost").exists()


@pytest.mark.django_db
def test_subscription_access(basic_plan):
    hospital = provision_hospital(
        name="Access Hospital",
        email="access@test.hospital",
        subdomain="access",
        base_domain="localhost",
    )
    sub = hospital.subscription
    assert sub.is_access_allowed() is True

    sub.status = Subscription.Status.CANCELED
    sub.save()
    assert sub.is_access_allowed() is False
