"""
Alembic environment configuration for async SQLModel migrations.
"""

from logging.config import fileConfig
from sqlalchemy import pool, engine_from_config
from sqlalchemy.engine import Connection
from alembic import context

from sqlmodel import SQLModel

# Import app config
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1]))

from app.config import settings

# Import all models here to ensure they're registered with SQLModel
from app.models.user import User
from app.models.task import Task

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel metadata
target_metadata = SQLModel.metadata

# Database URL from settings (use psycopg2 for sync)
DATABASE_URL = settings.database_url.replace(
    "postgresql://", "postgresql+psycopg2://"
)

# Update the sqlalchemy.url in alembic.ini
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL
    
    connectable = engine_from_config(
        configuration,
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

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
