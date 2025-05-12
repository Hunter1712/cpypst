import sqlite3
import threading

# Lock for DB access
db_lock = threading.Lock()


def create_database_connection(db_name):
    """Create a database connection."""
    try:
        conn = sqlite3.connect(db_name, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(f"Error creating database connection: {e}")
        return None


def create_database_table(conn):
    """Create the file_operations table in the database if it does not exist."""
    try:
        with db_lock:  # Ensure no other thread writes to the database while this runs
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_operations (
                id INTEGER PRIMARY KEY,
                source_path TEXT,
                destination_path TEXT,
                operation TEXT,
                status TEXT,
                error TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating database table: {e}")


def log_operation(conn, src, dest, operation, status, error=None):
    """Log file operation details into the database."""
    try:
        with db_lock:  # Ensure no other thread writes to the database while this runs
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO file_operations (source_path, destination_path, operation, status, error)
            VALUES (?, ?, ?, ?, ?)
            ''', (src, dest, operation, status, error))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error logging operation: {e}")
