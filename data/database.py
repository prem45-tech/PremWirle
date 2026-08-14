import sqlite3
import pandas as pd
from pathlib import Path
import hashlib


DB_PATH = "data/finance.db"



# DATABASE CONNECTION

def get_connection():
    Path("data").mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)



# CREATE DATABASE


def create_database():

    conn = get_connection()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Transactions table
    conn.execute("""
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

    conn.commit()
    conn.close()



# PASSWORD HASHING


def hash_password(password):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()



# REGISTER USER


def register_user(name, email, password):

    conn = get_connection()

    hashed_password = hash_password(password)

    try:

        conn.execute("""
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
        """, (
            name,
            email,
            hashed_password
        ))

        conn.commit()
        conn.close()

        return True

    except sqlite3.IntegrityError:

        conn.close()

        return False



# LOGIN USER


def login_user(email, password):

    conn = get_connection()

    hashed_password = hash_password(password)

    user = conn.execute("""
        SELECT id, name, email
        FROM users
        WHERE email = ?
        AND password = ?
    """, (
        email,
        hashed_password
    )).fetchone()

    conn.close()

    return user



# ADD TRANSACTION


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



# GET USER TRANSACTIONS


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



# DELETE TRANSACTION


def delete_transaction(transaction_id, user_id):

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