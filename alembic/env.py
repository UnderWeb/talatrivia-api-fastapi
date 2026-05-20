# alembic/env.py
"""Alembic environment configuration."""

import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

import app.models  # noqa: F401
from alembic import context
from app.core.config import settings
from app.db.base import Base

# Alembic config object
config = context.config

# ------------------------------------------------------
# Logging setup (safe for Docker / missing config)
# ------------------------------------------------------
if config.config_file_name and os.path.exists(config.config_file_name):
    fileConfig(config.config_file_name)

# ------------------------------------------------------
# Database URL (must be STRING for configparser)
# ------------------------------------------------------
config.set_main_option(
    "sqlalchemy.url",
    str(settings.DATABASE_URL),
)

# ------------------------------------------------------
# Target metadata (required for autogenerate)
# ------------------------------------------------------
target_metadata = Base.metadata


# ------------------------------------------------------
# OFFLINE MIGRATIONS
# ------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (SQL generation only)."""
    context.configure(
        url=str(settings.DATABASE_URL),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------------------------------------
# ONLINE MIGRATIONS
# ------------------------------------------------------
def run_migrations_online() -> None:
    """Run migrations in 'online' mode (direct DB execution)."""

    connectable = create_engine(
        str(settings.DATABASE_URL),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            include_schemas=True,
            render_as_batch=False,
        )

        with context.begin_transaction():
            context.run_migrations()


# ------------------------------------------------------
# ENTRYPOINT
# ------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
