from typing import Any, Mapping, Sequence, Optional, TypeAlias
import psycopg2
from psycopg2.extras import RealDictCursor

_SQLParams: TypeAlias = Sequence[Any] | Mapping[str, Any]


def fetch_all(
    connection: psycopg2.extensions.connection,
    query: str,
    params: Optional[_SQLParams] = None,
):
    """
    Helper for read operations that should return many rows.
    """
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        return cursor.fetchall()


def fetch_one(
    connection: psycopg2.extensions.connection,
    query: str,
    params: Optional[_SQLParams] = None,
):
    """
    Helper for read operations that should return a single row.
    """
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        return cursor.fetchone()


def execute_returning(
    connection: psycopg2.extensions.connection,
    query: str,
    params: Optional[_SQLParams] = None,
):
    """
    Executes a statement that returns data (e.g. INSERT ... RETURNING ...).
    """
    with connection:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            return cursor.fetchone()


def execute_with_row_count(
    connection: psycopg2.extensions.connection,
    query: str,
    params: Optional[_SQLParams] = None,
):
    """
    Executes a statement where we only care about the affected row count.
    """
    with connection:
        with connection.cursor() as cursor:
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            return cursor.rowcount
