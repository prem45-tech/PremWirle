import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = "data/finance.db"


def create_database():
    Path("data").mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_transaction(transaction_type, amount, category, date, description):
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        INSERT INTO transactions
        (transaction_type, amount, category, date, description)
        VALUES (?, ?, ?, ?, ?)
    """, (
        transaction_type,
        amount,
        category,
        date,
        description
    ))

    conn.commit()
    conn.close()


def get_transactions():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        "SELECT * FROM transactions ORDER BY date DESC",
        conn
    )

    conn.close()

    return df


def delete_transaction(transaction_id):
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        "DELETE FROM transactions WHERE id = ?",
        (transaction_id,)
    )

    conn.commit()
    conn.close()