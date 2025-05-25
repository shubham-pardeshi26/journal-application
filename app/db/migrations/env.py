from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from app.core.config import settings # <--- This is key
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_url():
    """
    Get the database URL from your application's settings.
    """
    # This accesses the DATABASE_URL property from your loaded settings object
    return settings.DATABASE_URL

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

import os
import sys
from pathlib import Path

# Add the project root to the sys.path to allow absolute imports like 'app.core.config'
# This assumes you are running alembic commands from the project root directory
sys.path.append(str(Path(__file__).resolve().parents[3]))


from app.core.database import Base # Import your Base
from app.core.config import settings # Import your settings

# Import all your models here so Alembic can discover them
# The __init__.py in app/db/models should handle importing all individual models
from app.db.models import user, group, journal, comment, media # Or just 'from app.db import models' if models/__init__.py imports everything

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    url = get_url()
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = url
    connectable = engine_from_config(
        configuration=configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
