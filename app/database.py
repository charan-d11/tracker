import os
from contextlib import contextmanager

import psycopg2
import psycopg2.extras
from psycopg2 import errors
from dotenv import load_dotenv
load_dotenv() 
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set (check your .env file)")

@contextmanager
def get_cursor():
    """Open a connection, give a dict cursor, commit on success, rollback on error."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_cursor() as cur:
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS pots (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                balance NUMERIC(12,2) NOT NULL DEFAULT 0
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                item TEXT NOT NULL,
                amount NUMERIC(12,2) NOT NULL,
                bought_by TEXT NOT NULL,
                date TIMESTAMPTZ DEFAULT NOW()
            )
        ''')


# ---------- Users ----------

def create_user(username, password_hash):
    """Returns the new user's id, or None if the username is taken."""
    try:
        with get_cursor() as cur:
            cur.execute(
                'INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id',
                (username, password_hash)
            )
            user_id = cur.fetchone()["id"]
            # every user gets their own pot
            cur.execute('INSERT INTO pots (user_id, balance) VALUES (%s, 0)', (user_id,))
            return user_id
    except errors.UniqueViolation:
        return None


def get_user_by_username(username):
    with get_cursor() as cur:
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        return cur.fetchone()


def get_user_by_id(user_id):
    with get_cursor() as cur:
        cur.execute('SELECT id, username FROM users WHERE id = %s', (user_id,))
        return cur.fetchone()


# ---------- Members ----------

def save_members(user_id, names):
    """Replace the user's member list with the given names."""
    with get_cursor() as cur:
        cur.execute('DELETE FROM members WHERE user_id = %s', (user_id,))
        for name in names:
            cur.execute(
                'INSERT INTO members (user_id, name) VALUES (%s, %s)',
                (user_id, name)
            )


def get_members(user_id):
    with get_cursor() as cur:
        cur.execute('SELECT name FROM members WHERE user_id = %s ORDER BY id', (user_id,))
        return [row["name"] for row in cur.fetchall()]


# ---------- Pot ----------

def get_balance(user_id):
    with get_cursor() as cur:
        cur.execute('SELECT balance FROM pots WHERE user_id = %s', (user_id,))
        row = cur.fetchone()
        return float(row["balance"]) if row else 0.0


def add_money(user_id, amount):
    with get_cursor() as cur:
        cur.execute(
            'UPDATE pots SET balance = balance + %s WHERE user_id = %s',
            (amount, user_id)
        )


def reset_pot(user_id):
    with get_cursor() as cur:
        cur.execute('UPDATE pots SET balance = 0 WHERE user_id = %s', (user_id,))


# ---------- Purchases ----------

def add_purchase(user_id, item, amount, bought_by):
    """Returns True on success, False if the pot doesn't have enough money.
    The balance check and subtraction happen in one atomic statement."""
    with get_cursor() as cur:
        cur.execute(
            'UPDATE pots SET balance = balance - %s '
            'WHERE user_id = %s AND balance >= %s RETURNING balance',
            (amount, user_id, amount)
        )
        if cur.fetchone() is None:
            return False
        cur.execute(
            'INSERT INTO purchases (user_id, item, amount, bought_by) '
            'VALUES (%s, %s, %s, %s)',
            (user_id, item, amount, bought_by)
        )
        return True


def get_purchases(user_id):
    with get_cursor() as cur:
        cur.execute(
            'SELECT item, amount, bought_by, date FROM purchases '
            'WHERE user_id = %s ORDER BY date DESC',
            (user_id,)
        )
        rows = cur.fetchall()
    return [
        {
            "item": r["item"],
            "amount": float(r["amount"]),
            "bought_by": r["bought_by"],
            "date": r["date"].isoformat(),
        }
        for r in rows
    ]


def clear_purchases(user_id):
    with get_cursor() as cur:
        cur.execute('DELETE FROM purchases WHERE user_id = %s', (user_id,))