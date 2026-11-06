# ruff: noqa: S105, PLR2004, PLC0415
from __future__ import annotations

import importlib
import os
from unittest import mock


def test_production_settings_databases_and_cache_with_database_url():
    env_vars = {
        "DJANGO_SETTINGS_MODULE": "config.settings.production",
        "DJANGO_SECRET_KEY": "dummy-secret-key-for-testing-production-settings-only",
        "DJANGO_ADMIN_URL": "admin/",
        "DATABASE_URL": "postgres://test_user:test_password@db_host:5432/test_dbname",
        "REDIS_URL": "redis://redis_host:6379/2",
    }
    with mock.patch.dict(os.environ, env_vars, clear=False):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)

        db_default = prod_settings.DATABASES["default"]
        assert db_default["ENGINE"] == "django.db.backends.postgresql"
        assert db_default["NAME"] == "test_dbname"
        assert db_default["USER"] == "test_user"
        assert db_default["PASSWORD"] == "test_password"
        assert db_default["HOST"] == "db_host"
        assert db_default["PORT"] == 5432
        assert db_default["ATOMIC_REQUESTS"] is True
        assert db_default["CONN_MAX_AGE"] == 60

        cache_default = prod_settings.CACHES["default"]
        assert cache_default["BACKEND"] == "django_redis.cache.RedisCache"
        assert cache_default["LOCATION"] == "redis://redis_host:6379/2"
        assert cache_default["OPTIONS"]["CLIENT_CLASS"] == "django_redis.client.DefaultClient"


def test_production_settings_databases_fallback_to_postgres_env():
    env_vars = {
        "DJANGO_SETTINGS_MODULE": "config.settings.production",
        "DJANGO_SECRET_KEY": "dummy-secret-key-for-testing-production-settings-only",
        "DJANGO_ADMIN_URL": "admin/",
        "POSTGRES_HOST": "postgres_service",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DB": "custom_prod_db",
        "POSTGRES_USER": "prod_user",
        "POSTGRES_PASSWORD": "prod_password",
        "REDIS_URL": "redis://redis_service:6379/0",
    }
    # Ensure DATABASE_URL is not present
    filtered_env = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}
    filtered_env.update(env_vars)

    with mock.patch.dict(os.environ, filtered_env, clear=True):
        import config.settings.production as prod_settings

        importlib.reload(prod_settings)

        db_default = prod_settings.DATABASES["default"]
        assert db_default["ENGINE"] == "django.db.backends.postgresql"
        assert db_default["NAME"] == "custom_prod_db"
        assert db_default["USER"] == "prod_user"
        assert db_default["PASSWORD"] == "prod_password"
        assert db_default["HOST"] == "postgres_service"
        assert db_default["PORT"] == 5432
        assert db_default["ATOMIC_REQUESTS"] is True
