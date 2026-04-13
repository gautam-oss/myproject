# Hospital SaaS — Multi-Tenant Platform

A multi-tenant SaaS platform for hospitals built on Django + PostgreSQL (schema-per-tenant).

## Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.1, Django REST Framework |
| Multi-tenancy | django-tenants (schema-per-tenant) |
| Database | PostgreSQL 16 |
| Cache / Queue | Redis 7 + Celery |
| Auth | JWT (SimpleJWT) |
| Payments | Stripe |
| Containers | Docker + Docker Compose |

---

## Fedora 43 — First-time setup

### 1. Install Docker

```bash
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker          # apply group without logging out
```

### 2. Install Python dev tools

```bash
sudo dnf install -y python3.12 python3.12-devel gcc libpq-devel
```

### 3. Clone and configure

```bash
git clone <your-repo-url> myproject
cd myproject
cp .env.example config/env/.env.dev
# Edit config/env/.env.dev and fill in your Stripe test keys
```

### 4. Build and start

```bash
make build
make up
make migrate          # runs migrate_schemas --shared then all tenants
make createsuperuser
```

### 5. Create a demo hospital tenant

```bash
make demo-tenant
```

This provisions `demo.localhost` → `hospital_demo` schema in PostgreSQL.

### 6. Test subdomain routing locally

Add to `/etc/hosts`:
```
127.0.0.1  demo.localhost
```

Then visit `http://demo.localhost:8000/api/v1/auth/token/` — you're inside the demo hospital's schema.

---

## Daily workflow

```bash
make up               # start everything
make logs             # tail logs
make shell            # Django shell inside web container
make migrate          # after pulling new migrations
make test             # run pytest
make down             # stop everything
```

---

## Project structure

```
apps/
  tenants/     # Hospital, Domain, Plan, Subscription — public schema
  users/       # Custom User model with RBAC roles — public schema
  patients/    # EHR, Patient, MedicalRecord — tenant schema
  scheduling/  # Appointment, StaffShift — tenant schema
  billing/     # Invoice, Payment — tenant schema
  api/         # DRF URL routing
  core/        # Shared utilities, base models

config/
  django/settings/   # base / dev / staging / production
  compose/           # docker-compose files per environment
  docker/            # Dockerfile, entrypoint, start scripts
  env/               # .env files (gitignored)
  nginx/             # Nginx configs
  gunicorn/          # Gunicorn config
```

---

## Tenant provisioning

To create a new hospital programmatically:

```python
from apps.tenants.services import provision_hospital
from apps.tenants.models import Plan

hospital = provision_hospital(
    name="Nairobi General Hospital",
    email="admin@nairobi-general.ke",
    subdomain="nairobi",
    plan_tier=Plan.Tier.PRO,
    base_domain="yoursaas.com",
    trial_days=14,
)
# → creates PostgreSQL schema hospital_nairobi_general_hospital
# → creates domain nairobi.yoursaas.com
# → creates Subscription(status=TRIALING)
```

---

## Environment variables

See `.env.example` for all required variables. Never commit real secrets.
