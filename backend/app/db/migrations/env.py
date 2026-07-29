import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Alembic config object
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import ALL models so their metadata is registered with Base
# ---------------------------------------------------------------------------
from app.db.base import Base  # noqa: E402
import app.models  # noqa: E402, F401  — registers URL, User

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# DB URL — override alembic.ini placeholder with env var, converting the
# async asyncpg driver to the sync psycopg driver for Alembic.
# ---------------------------------------------------------------------------

def get_sync_url() -> str:
    url = os.environ.get("DATABASE_URL", config.get_main_option("sqlalchemy.url", ""))
    # Alembic runs sync migrations; replace async driver with sync psycopg
    return (
        url
        .replace("postgresql+asyncpg://", "postgresql+psycopg://")
        .replace("postgresql+aiopg://", "postgresql+psycopg://")
    )


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL script)."""
    context.configure(
        url=get_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live DB connection."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_sync_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
