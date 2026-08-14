import sqlite3
import pandas as pd
import hashlib
from pathlib import Path


DB_PATH = "data/finance.db"


def get_connection():
    Path("data").mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def create_database():

    conn = get_connection()

    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    """)

    # Transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Check users columns
    cursor.execute(
        "PRAGMA table_info(users)"
    )

    user_columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "is_admin" not in user_columns:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN is_admin INTEGER DEFAULT 0
        """)

    # Check transactions columns
    cursor.execute(
        "PRAGMA table_info(transactions)"
    )

    transaction_columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "user_id" not in transaction_columns:

        cursor.execute("""
            ALTER TABLE transactions
            ADD COLUMN user_id INTEGER
        """)

    # Create default admin
    admin_email = "premwirle@gmail.com"
    admin_password = "admin123"

    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (admin_email,)
    )

    admin_exists = cursor.fetchone()

    if not admin_exists:

        cursor.execute("""
            INSERT INTO users
            (name, email, password, is_admin)
            VALUES (?, ?, ?, ?)
        """, (
            "Administrator",
            admin_email,
            hash_password(admin_password),
            1
        ))

    conn.commit()
    conn.close()


def register_user(
    name,
    email,
    password
):

    conn = get_connection()

    try:

        conn.execute("""
            INSERT INTO users
            (name, email, password, is_admin)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            hash_password(password),
            0
        ))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def login_user(
    email,
    password
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            is_admin
        FROM users
        WHERE email = ?
        AND password = ?
    """, (
        email,
        hash_password(password)
    ))

    user = cursor.fetchone()

    conn.close()

    return user


def add_transaction(
    user_id,
    transaction_type,
    amount,
    category,
    date,
    description
):

    conn = get_connection()

    conn.execute("""
        INSERT INTO transactions
        (
            user_id,
            transaction_type,
            amount,
            category,
            date,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        transaction_type,
        amount,
        category,
        date,
        description
    ))

    conn.commit()
    conn.close()


def get_transactions(user_id):

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            id,
            transaction_type,
            amount,
            category,
            date,
            description
        FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC
    """, conn, params=(user_id,))

    conn.close()

    return df


def delete_transaction(
    transaction_id,
    user_id
):

    conn = get_connection()

    conn.execute("""
        DELETE FROM transactions
        WHERE id = ?
        AND user_id = ?
    """, (
        transaction_id,
        user_id
    ))

    conn.commit()
    conn.close()


def get_all_users():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            id,
            name,
            email,
            is_admin
        FROM users
        ORDER BY id
    """, conn)

    conn.close()

    # Make admin status easier to understand
    df["is_admin"] = df["is_admin"].map({
        1: "Yes",
        0: "No"
    })

    return df


def get_all_transactions():

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT
            transactions.id,
            transactions.user_id,
            users.name AS user_name,
            users.email AS user_email,
            transactions.transaction_type,
            transactions.amount,
            transactions.category,
            transactions.date,
            transactions.description

        FROM transactions

        INNER JOIN users
        ON transactions.user_id = users.id

        ORDER BY transactions.date DESC
    """, conn)

    conn.close()

    return df