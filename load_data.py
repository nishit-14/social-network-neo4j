"""Load processed CSV files into Neo4j."""

from pathlib import Path

import pandas as pd
from neo4j.exceptions import Neo4jError

from db import get_connection


USERS_PATH = Path("data/processed/users.csv")
FOLLOWS_PATH = Path("data/processed/follows.csv")
BATCH_SIZE = 1_000


def chunked(records, size=BATCH_SIZE):
    for index in range(0, len(records), size):
        yield records[index : index + size]


def confirm_clear_database():
    answer = input("Clear existing User nodes and FOLLOWS relationships? (y/N): ")
    return answer.strip().lower() == "y"


def create_constraints(conn):
    queries = [
        """
        CREATE CONSTRAINT user_id_unique IF NOT EXISTS
        FOR (u:User)
        REQUIRE u.userId IS UNIQUE
        """,
        """
        CREATE CONSTRAINT username_unique IF NOT EXISTS
        FOR (u:User)
        REQUIRE u.username IS UNIQUE
        """,
    ]
    for query in queries:
        conn.execute_write(query)


def clear_database(conn):
    conn.execute_write("MATCH (:User)-[r:FOLLOWS]->(:User) DELETE r")
    conn.execute_write("MATCH (u:User) DELETE u")


def load_users(conn, users_path=USERS_PATH):
    users = pd.read_csv(users_path, dtype=str).fillna("").to_dict("records")
    query = """
    UNWIND $rows AS row
    MERGE (u:User {userId: row.userId})
    SET u.name = row.name,
        u.username = row.username,
        u.email = row.email,
        u.password = row.password,
        u.bio = row.bio
    """
    for batch in chunked(users):
        conn.execute_write(query, rows=batch)
    return len(users)


def load_follows(conn, follows_path=FOLLOWS_PATH):
    follows = pd.read_csv(follows_path, dtype=str).drop_duplicates().to_dict("records")
    query = """
    UNWIND $rows AS row
    MATCH (source:User {userId: row.source})
    MATCH (target:User {userId: row.target})
    WHERE source <> target
    MERGE (source)-[:FOLLOWS]->(target)
    """
    for batch in chunked(follows):
        conn.execute_write(query, rows=batch)
    return len(follows)


def validate_files():
    missing = [str(path) for path in [USERS_PATH, FOLLOWS_PATH] if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing processed CSV file(s): "
            + ", ".join(missing)
            + "\nRun: python process_dataset.py"
        )


def main():
    conn = None
    try:
        validate_files()
        conn = get_connection()

        if confirm_clear_database():
            print("Clearing old data...")
            clear_database(conn)
        else:
            print("Keeping existing data. MERGE will avoid duplicate users/follows.")

        print("Creating constraints...")
        create_constraints(conn)

        print("Loading users...")
        user_count = load_users(conn)

        print("Loading FOLLOWS relationships...")
        follow_count = load_follows(conn)

        print("Load complete.")
        print(f"Users loaded from CSV: {user_count:,}")
        print(f"FOLLOWS relationships loaded from CSV: {follow_count:,}")
    except (FileNotFoundError, RuntimeError, Neo4jError) as exc:
        print(f"Load failed: {exc}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
