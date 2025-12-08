import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_NAME = os.getenv("DATABASE_NAME")
PASSWORD = os.getenv("PASSWORD")


def get_connection():
    """
    Function that returns a single connection
    In reality, we might use a connection pool, since
    this way we'll start a new connection each time
    someone hits one of our endpoints, which isn't great for performance
    """
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user="postgres",  # change if needed
        password=PASSWORD,
        host="localhost",  # change if needed
        port="5432",  # change if needed
    )


def _create_tables() -> bool:
    """
    A function to create the necessary tables for the project.
    """
    connection = get_connection()
    with connection, connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INT NOT NULL
            );
        """)
        cursor.execute("SELECT version FROM schema_version")

        version = cursor.fetchone()

        if version is not None and version[0] >= 1:
            return False

        with open("schema.sql", "r", encoding="utf-8") as f:
            sql = f.read()

        statements = [s.strip() for s in sql.split(";") if s.strip()]

        for statement in statements:
            cursor.execute(statement)

        cursor.execute("""
            INSERT INTO schema_version (version) VALUES (1)
            ON CONFLICT DO NOTHING;
        """)

        return True


def _seed_tables():
    """
    A function to seed database data
    """
    connection = get_connection()
    with connection, connection.cursor() as cursor:
        with open("seed_inserts.sql", "r", encoding="utf-8") as f:
            sql = f.read()

        statements = [s.strip() for s in sql.split(";") if s.strip()]

        for statement in statements:
            cursor.execute(statement)


def run_setup():
    if _create_tables():
        _seed_tables()
