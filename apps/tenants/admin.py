from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Hospital, Domain, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "tier", "price_monthly", "max_users", "max_patients",
                    "has_billing_module", "has_analytics"]
    list_editable = ["price_monthly"]


class DomainInline(admin.TabularInline):
    model = Domain
    extra = 1


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0


@admin.register(Hospital)
class HospitalAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ["name", "schema_name", "email", "is_active", "on_trial", "created_at"]
    list_filter = ["is_active", "on_trial"]
    search_fields = ["name", "email", "schema_name"]
    inlines = [DomainInline, SubscriptionInline]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["hospital", "plan", "status", "current_period_end"]
    list_filter = ["status", "plan"]
    search_fields = ["hospital__name", "stripe_customer_id"]
