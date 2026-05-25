"""
alembic/env.py — Alembic migration environment.

What it does:
  Configures Alembic to connect to the database using DATABASE_URL from
  the environment and run migrations against our SQLAlchemy metadata.

Why it exists at this layer:
  Alembic requires this file to know how to connect and what schema to
  manage. We override the default to pull credentials from the environment
  rather than hardcoding them in alembic.ini, following 12-factor app
  principles.

How it connects:
  - Reads DATABASE_URL from environment (set in .env or CI secrets).
  - Imports Base.metadata from app/models/base.py so autogenerate can
    diff the current schema against our SQLAlchemy models.
  - Run via: alembic upgrade head
"""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Alembic Config object — gives access to alembic.ini values
config = context.config

# Set up Python logging from alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Model metadata — import Base so autogenerate sees our table definitions
# ---------------------------------------------------------------------------
from app.models.base import Base  # noqa: E402
target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Database URL — from environment, never from alembic.ini
# ---------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL script)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
