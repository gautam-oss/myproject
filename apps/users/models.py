from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Single user model shared across all tenants (lives in public schema).
    Role determines what the user can do inside their hospital tenant.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        DOCTOR = "doctor", "Doctor"
        NURSE = "nurse", "Nurse"
        RECEPTIONIST = "receptionist", "Receptionist"
        BILLING_CLERK = "billing_clerk", "Billing clerk"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RECEPTIONIST)

    # Which hospital schema this user belongs to.
    # Storing schema_name (not a FK) because User is in the public schema
    # while hospital data lives in tenant schemas.
    tenant_schema = models.CharField(max_length=100, blank=True, db_index=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.full_name} <{self.email}> [{self.role}]"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    # ── Role helpers ──────────────────────────────────────────────────────────
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_doctor(self):
        return self.role == self.Role.DOCTOR

    @property
    def is_billing_clerk(self):
        return self.role == self.Role.BILLING_CLERK

    @property
    def can_view_patients(self):
        return self.role in (
            self.Role.ADMIN,
            self.Role.DOCTOR,
            self.Role.NURSE,
            self.Role.RECEPTIONIST,
        )

    @property
    def can_manage_billing(self):
        return self.role in (self.Role.ADMIN, self.Role.BILLING_CLERK)

    class Meta:
        ordering = ["email"]
