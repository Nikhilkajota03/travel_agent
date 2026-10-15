import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver

from src.config import settings

def get_database_url() -> str:
    """Helper to return the configured database URL."""
    return settings.get_database_url()

_checkpointer_instance: PostgresSaver | None = None
_db_connection = None


def get_checkpointer() -> PostgresSaver:
    """
    Lazily initialize and return the PostgresSaver checkpointer instance.
    Sets up the required PostgreSQL checkpoint tables on first run.
    """
    global _checkpointer_instance, _db_connection
    if _checkpointer_instance is None:
        db_url = settings.get_database_url()
        _db_connection = psycopg.connect(
            db_url,
            autocommit=True,
            row_factory=dict_row,
        )
        _checkpointer_instance = PostgresSaver(_db_connection)
        _checkpointer_instance.setup()

    return _checkpointer_instance
