import sqlite3

DB_NAME = "tracker.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # so we get dict-like rows
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Pot table — stores the shared money balance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            balance REAL NOT NULL DEFAULT 0
        )
    ''')

    # Insert a default pot if none exists
    cursor.execute('SELECT COUNT(*) FROM pot')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO pot (balance) VALUES (0)')

    # Purchases table — stores every purchase
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            bought_by TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def get_balance():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM pot WHERE id = 1')
    row = cursor.fetchone()
    conn.close()
    return row["balance"] if row else 0


def add_money(amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE pot SET balance = balance + ? WHERE id = 1', (amount,))
    conn.commit()
    conn.close()


def add_purchase(item, amount, bought_by):
    conn = get_connection()
    cursor = conn.cursor()

    # Subtract from pot
    cursor.execute('UPDATE pot SET balance = balance - ? WHERE id = 1', (amount,))

    # Log the purchase
    cursor.execute(
        'INSERT INTO purchases (item, amount, bought_by) VALUES (?, ?, ?)',
        (item, amount, bought_by)
    )

    conn.commit()
    conn.close()


def get_purchases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM purchases ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_purchases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM purchases')
    conn.commit()
    conn.close()

def reset_pot():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE pot SET balance = 0 WHERE id = 1')
    conn.commit()
    conn.close()