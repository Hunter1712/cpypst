import sqlite3
import threading

db_lock = threading.Lock()


def create_database_connection(db_name):
    try:
        return sqlite3.connect(db_name, check_same_thread=False)
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


def create_database_table(conn):
    try:
        with db_lock:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_path TEXT,
                    destination_path TEXT,
                    operation TEXT,
                    status TEXT,
                    error TEXT,
                    source_checksum TEXT,
                    destination_checksum TEXT,
                    file_size INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")


def log_operation(conn, src, dest, operation, status,
                  error=None, src_checksum=None, dest_checksum=None, file_size=None):
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO file_operations 
            (source_path, destination_path, operation, status, error, 
             source_checksum, destination_checksum, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (src, dest, operation, status, error, src_checksum, dest_checksum, file_size))
        with db_lock:
            conn.commit()
    except sqlite3.Error as e:
        print(f"Logging error: {e}")
