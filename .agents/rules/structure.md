---
trigger: always_on
---

# Incienso Shop: Codebase Structure & Directory Layout

## Directory Boundaries

```text
incienso-shop/
├── config/                         # Django global configuration
│   ├── settings/                   # base.py, local.py, production.py, test.py
│   ├── urls.py                     # Root URL router
│   ├── celery_app.py               # Celery application instance
│   ├── wsgi.py / asgi.py           # WSGI/ASGI entrypoints
│   └── api_router.py               # DRF API router
│
├── incienso_shop/                  # Main application package
│   ├── apps/                       # Modular monolith applications
│   │   ├── core/                   # Shared infrastructure (BaseModel, StoreSettings, exceptions, cache helpers)
│   │   ├── users/                  # Custom User identity & profile
│   │   ├── products/               # Product catalog, categories, aroma families, inventory
│   │   ├── orders/                 # Shopping cart (Cart, CartItem) and Orders (Order, OrderItem)
│   │   ├── payments/               # Payment gateway integration with django-payments (Payment model)
│   │   ├── reviews/                # Product reviews, ratings and testimonials
│   │   ├── audit/                  # Audit trail viewer & security/activity events (django-simple-history)
│   │   ├── logs/                   # Application log analyzer, parser & viewer
│   │   ├── monitor/                # Instance health, SQLite WAL/DB connection stats & DiskCache metrics
│   │   └── backups/                # SQLite online backups, retention & restore management
│   │
│   ├── static/                     # Global static assets (css/project.css, js/project.js, images/)
│   ├── templates/                  # Global templates (base.html, pages/home.html, pages/about.html, etc.)
│   └── contrib/                    # Contrib sites migrations
│
├── compose/                        # Docker entrypoint & startup scripts
├── tests/                          # Root integration & configuration tests
├── docs/                           # Sphinx documentation
├── locale/                         # Internationalization catalogs
└── pyproject.toml                  # Python 3.14 packaging & uv dependencies
```

## Standard Application Internal Structure

Each application inside `incienso_shop/apps/<app_name>/` must follow the clean layered architecture:

```text
incienso_shop/apps/<app_name>/
├── __init__.py
├── admin.py            # ModelAdmin registrations with SimpleHistoryAdmin
├── apps.py             # AppConfig declaration with unique label
├── choices.py          # models.TextChoices / IntegerChoices
├── exceptions.py       # Domain-specific exceptions inheriting from BusinessLogicError
├── filters.py          # django-filter FilterSet classes
├── forms.py            # Crispy Forms (Bootstrap 5)
├── models.py           # Django Models (Auditlog registered, HistoricalRecords)
├── selectors.py        # Read-only business queries & DiskCache access
├── services.py         # Write/mutation business logic & @transaction.atomic
├── tables.py           # django-tables2 Table definitions
├── tasks.py            # Celery asynchronous tasks
├── urls.py             # App URL patterns with namespace
├── views.py            # Class-Based Views (CBVs) with Unpoly support
├── api/                # DRF serializers and ViewSets (optional)
├── templates/          # App-specific HTML templates
└── tests/              # Pytest unit & integration tests
```
