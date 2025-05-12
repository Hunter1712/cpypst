import sqlite3


def create_database_connection(db_name):
    try:
        return sqlite3.connect(db_name)
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


def create_database_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_path TEXT,
            destination_path TEXT,
            operation TEXT,
            status TEXT,
            error TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()


def log_operation(cursor, src, dest, operation, status, error=None):
    cursor.execute('''
        INSERT INTO file_operations (source_path, destination_path, operation, status, error)
        VALUES (?, ?, ?, ?, ?)
    ''', (src, dest, operation, status, error))
    cursor.connection.commit()


def check_file_status(cursor, src_path):
    cursor.execute('''
        SELECT status FROM file_operations
        WHERE source_path = ?
        ORDER BY timestamp DESC LIMIT 1
    ''', (src_path,))
    row = cursor.fetchone()
    return row[0] if row else None
