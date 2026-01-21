"""Generic single-database configuration."""
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# Load environment variables
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models for autogenerate support
from app.models import Base

target_metadata = Base.metadata

# Determine if we should use schema (PostgreSQL) or not (SQLite)
database_url_check = os.getenv("DATABASE_URL", "")
if not database_url_check:
    database_url_check = config.get_main_option("sqlalchemy.url", "")
use_schema = database_url_check.startswith("postgresql")

# Override sqlalchemy.url with environment variable if it's PostgreSQL
# This allows DATABASE_URL to override prod config when set
database_url = os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgresql"):
    # Use standard psycopg2 for PostgreSQL synchronous operations
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")
    config.set_main_option("sqlalchemy.url", database_url)
elif not config.get_main_option("sqlalchemy.url"):
    # If no DATABASE_URL and no sqlalchemy.url in config, raise error
    raise ValueError(
        "DATABASE URL not configured. Either:\n"
        "  1. Use named section: alembic -n test upgrade head\n"
        "  2. Set DATABASE_URL environment variable\n"
        "  3. Set sqlalchemy.url in alembic.ini"
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context_kwargs = {
        "url": url,
        "target_metadata": target_metadata,
        "literal_binds": True,
        "dialect_opts": {"paramstyle": "named"},
    }

    # Add schema configuration only for PostgreSQL
    if use_schema:
        context_kwargs["version_table_schema"] = "grocery_service"
        context_kwargs["include_schemas"] = True

    context.configure(**context_kwargs)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context_kwargs = {
            "connection": connection,
            "target_metadata": target_metadata,
        }

        # Add schema configuration only for PostgreSQL
        if use_schema:
            context_kwargs["version_table_schema"] = "grocery_service"
            context_kwargs["include_schemas"] = True

        context.configure(**context_kwargs)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
