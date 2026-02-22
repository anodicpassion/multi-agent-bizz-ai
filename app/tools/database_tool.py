"""Database query tool — uses an in-memory SQLite store for demo purposes."""

from __future__ import annotations

import json
import sqlite3
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

# ── Bootstrap a tiny in-memory business DB ────────────────────────────

_conn = sqlite3.connect(":memory:", check_same_thread=False)
_conn.row_factory = sqlite3.Row

_conn.executescript(
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        company TEXT,
        status TEXT DEFAULT 'active'
    );
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(id),
        product TEXT NOT NULL,
        amount REAL NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        assigned_to TEXT,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'open',
        created_at TEXT DEFAULT (datetime('now'))
    );

    -- Seed data
    INSERT INTO customers (name, email, company, status) VALUES
        ('Alice Johnson', 'alice@acme.com', 'Acme Corp', 'active'),
        ('Bob Smith', 'bob@globex.com', 'Globex Inc', 'active'),
        ('Carol Williams', 'carol@initech.com', 'Initech', 'inactive');

    INSERT INTO orders (customer_id, product, amount, status) VALUES
        (1, 'Enterprise Plan', 4999.00, 'completed'),
        (1, 'Add-on: Analytics', 999.00, 'pending'),
        (2, 'Starter Plan', 499.00, 'completed'),
        (3, 'Enterprise Plan', 4999.00, 'cancelled');

    INSERT INTO tasks (title, assigned_to, priority, status) VALUES
        ('Q1 Sales Report', 'Alice Johnson', 'high', 'open'),
        ('Onboard Globex', 'Bob Smith', 'medium', 'in_progress'),
        ('Update pricing page', 'Carol Williams', 'low', 'open');
    """
)


@tool
def query_database(query: str) -> str:
    """Execute a read-only SQL query against the business database.

    The database contains tables: customers, orders, tasks.
    Only SELECT statements are allowed.

    Args:
        query: A SQL SELECT query.

    Returns:
        JSON array of result rows, or an error message.
    """
    normalized = query.strip().upper()
    if not normalized.startswith("SELECT"):
        return json.dumps(
            {"error": "Only SELECT queries are permitted for safety."}
        )

    try:
        cursor = _conn.execute(query)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return json.dumps(rows, indent=2, default=str)
    except Exception as exc:
        logger.exception("Database query failed")
        return json.dumps({"error": str(exc)})
