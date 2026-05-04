"""Neo4j database connection helpers for the console social network app."""

import os
from contextlib import contextmanager

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable


load_dotenv()


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")


class Neo4jConnection:
    """Small wrapper around the official Neo4j Python driver."""

    def __init__(self, uri=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD):
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None

    def connect(self):
        """Open and verify a Neo4j driver connection."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
            )
            self.driver.verify_connectivity()
            return self
        except ServiceUnavailable as exc:
            raise RuntimeError(
                f"Could not connect to Neo4j at {self.uri}. Is Neo4j running?"
            ) from exc
        except Neo4jError as exc:
            raise RuntimeError(f"Neo4j connection error: {exc}") from exc

    def close(self):
        if self.driver:
            self.driver.close()

    @contextmanager
    def session(self):
        if not self.driver:
            self.connect()
        session = self.driver.session(database=NEO4J_DATABASE)
        try:
            yield session
        finally:
            session.close()

    def execute_read(self, query, **parameters):
        with self.session() as session:
            result = session.run(query, **parameters)
            return [record.data() for record in result]

    def execute_write(self, query, **parameters):
        with self.session() as session:
            result = session.run(query, **parameters)
            return [record.data() for record in result]


def get_connection():
    """Factory used by app.py and load_data.py."""
    return Neo4jConnection().connect()
