# db_utils.py
import os
import sqlite3
import datetime
from file_utils import calculate_checksum


def create_database_connection(db_name):
    """Creates a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def create_database_table(conn):
    """Creates the file_operations table in the database if it does not exist."""
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT UNIQUE,  -- Enforce unique source paths
                destination_path TEXT,
                operation_type TEXT,
                timestamp DATETIME,
                file_size INTEGER,
                checksum TEXT,
                error TEXT,
                status TEXT DEFAULT 'pending'  -- 'pending', 'success', 'failed'
            )
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")
        conn.rollback()


def log_operation(cursor, source_path, destination_path, operation_type, error=None, status='pending'):
    """Logs a file operation to the database."""
    file_size = None
    checksum = None
    if operation_type == 'copy' and destination_path:
        try:
            file_size = os.path.getsize(destination_path)
            checksum = calculate_checksum(destination_path)
        except OSError as e:  # Include the error message
            file_size = None
            checksum = None
            error = str(e)  # Log the error message
    elif operation_type == 'delete' and source_path:
        try:
            file_size = os.path.getsize(source_path)
            checksum = calculate_checksum(source_path)
        except OSError as e:  # Include the error message
            file_size = None
            checksum = None
            error = str(e)  # Log the error message
    elif operation_type == 'skip':
        file_size = 0  # Or None, if your DB allows NULL
        checksum = 'N/A'  # Or None

    try:
        cursor.execute('''
            INSERT INTO file_operations (source_path, destination_path, operation_type, timestamp, file_size, checksum, error, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (source_path, destination_path, operation_type, datetime.datetime.now(), file_size, checksum, error, status))
    except sqlite3.IntegrityError:
        cursor.execute('''
            UPDATE file_operations
            SET destination_path = ?, operation_type = ?, timestamp = ?, 
                file_size = ?, checksum = ?, error = ?, status = ?
            WHERE source_path = ?
        ''', (destination_path, operation_type, datetime.datetime.now(), file_size, checksum, error, status, source_path))


def check_file_status(cursor, source_path):
    """Checks the status of a file operation in the database."""
    cursor.execute('''
        SELECT status FROM file_operations WHERE source_path = ?
    ''', (source_path,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return None
