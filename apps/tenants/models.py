from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Plan(models.Model):
    """SaaS subscription plan available to hospitals."""

    class Tier(models.TextChoices):
        BASIC = "basic", "Basic"
        PRO = "pro", "Pro"
        ENTERPRISE = "enterprise", "Enterprise"

    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=20, choices=Tier.choices, unique=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_price_id = models.CharField(max_length=100, blank=True)

    # Feature flags — checked in code with hospital.subscription.plan
    max_users = models.PositiveIntegerField(default=10)
    max_patients = models.PositiveIntegerField(default=500)
    has_billing_module = models.BooleanField(default=False)
    has_analytics = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (${self.price_monthly}/mo)"

    class Meta:
        ordering = ["price_monthly"]


class Hospital(TenantMixin):
    """
    Each Hospital is a PostgreSQL schema (tenant).
    The schema_name field comes from TenantMixin (e.g. 'hospital_nairobi').
    auto_create_schema=True tells django-tenants to CREATE SCHEMA on save.
    """

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)

    is_active = models.BooleanField(default=True)
    on_trial = models.BooleanField(default=True)
    trial_ends_on = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Required by TenantMixin
    auto_create_schema = True

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Domain(DomainMixin):
    """
    Maps a hostname to a Hospital tenant.
    E.g. domain='nairobi.yoursaas.com' → Hospital(schema_name='hospital_nairobi')
    DomainMixin adds: domain (CharField), tenant (FK), is_primary (BooleanField).
    """
    pass


class Subscription(models.Model):
    """Links a hospital to a Plan with Stripe tracking."""

    class Status(models.TextChoices):
        TRIALING = "trialing", "Trialing"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past due"
        CANCELED = "canceled", "Canceled"
        SUSPENDED = "suspended", "Suspended"

    hospital = models.OneToOneField(
        Hospital, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIALING)

    stripe_customer_id = models.CharField(max_length=100, blank=True)
    stripe_subscription_id = models.CharField(max_length=100, blank=True)

    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_access_allowed(self):
        return self.status in (self.Status.TRIALING, self.Status.ACTIVE)

    def __str__(self):
        return f"{self.hospital.name} — {self.plan.name} ({self.status})"

    class Meta:
        ordering = ["-created_at"]
