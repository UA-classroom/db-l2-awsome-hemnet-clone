from typing import Any, Mapping, Sequence, Optional, TypeAlias
import psycopg2
from psycopg2.extras import RealDictCursor

_SQLParams: TypeAlias = Sequence[Any] | Mapping[str, Any]

"""
This file is responsible for making database queries, which your fastapi endpoints/routes can use.
The reason we split them up is to avoid clutter in the endpoints, so that the endpoints might focus on other tasks 

- Try to return results with cursor.fetchall() or cursor.fetchone() when possible
- Make sure you always give the user response if something went right or wrong, sometimes 
you might need to use the RETURNING keyword to garantuee that something went right / wrong
e.g when making DELETE or UPDATE queries
- No need to use a class here
- Try to raise exceptions to make them more reusable and work a lot with returns
- You will need to decide which parameters each function should receive. All functions 
start with a connection parameter.
- Below, a few inspirational functions exist - feel free to completely ignore how they are structured
- E.g, if you decide to use psycopg3, you'd be able to directly use pydantic models with the cursor, these examples are however using psycopg2 and RealDictCursor
"""


def fetch_all(
    con: psycopg2.extensions.connection,
    query: str,
    params: Optional[_SQLParams] = None,
):
    """
    Helper for read operations that should return many rows.
    """
    with con.cursor(cursor_factory=RealDictCursor) as cursor:
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        return cursor.fetchall()


def fetch_one(
    con: psycopg2.extensions.connection,
    query: str,
    params: Optional[_SQLParams] = None,
):
    """
    Helper for read operations that should return a single row.
    """
    with con.cursor(cursor_factory=RealDictCursor) as cursor:
        if params is None:
            cursor.execute(query)
        else:
            cursor.execute(query, params)
        return cursor.fetchone()


def execute_returning(
    con: psycopg2.extensions.connection,
    query: str,
    params: Optional[_SQLParams] = None,
):
    """
    Executes a statement that returns data (e.g. INSERT ... RETURNING ...).
    """
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            if params is None:
                cursor.execute(query)
            else:
                cursor.execute(query, params)
            return cursor.fetchone()
