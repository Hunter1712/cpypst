# cpypst

## Automated File Copying and Deletion

A simple multithreaded tool to copy files or folders, verify them using checksums, and log everything into an SQLite database. It can also delete the original files after successful copying. Designed for ease of use with no external dependencies.

## Features

- Copies files or entire directories
- Verifies integrity using SHA-256 checksums
- Retries failed copies up to 3 times
- Logs all actions (success, failure, skip, etc.) to an SQLite database
- Thread-safe database access
- Modular, easy-to-read Python code

## How It Works

1. The database is created if it doesn't already exist.
2. For each file or directory:
   - It checks if the destination already exists.
   - If not, it attempts to copy.
   - If the item is a file, it compares SHA-256 checksums.
   - On checksum mismatch, it retries up to 3 times.
   - Success or failure is logged in the database.
   - Successfully copied files are optionally deleted.

## File Structure

- **db_utils.py** – Manages database connections and logging
- **file_utils.py** – Handles copying, deleting, and checksumming files/directories
- **main_utils.py** – Core logic for processing files with retries and logging

## Requirements

- Python 3.8 or newer
- Standard Python libraries only:
  - `os`, `shutil`, `sqlite3`, `hashlib`, `threading`, `time`

## Database Log Format

Each operation is stored in the `file_operations` table with:

- `source_path`
- `destination_path`
- `operation` (copy, skip, cleanup)
- `status` (success, failed, skipped)
- `error` (if any)
- `source_checksum`
- `destination_checksum`
- `file_size`
- `timestamp`

## License

MIT License — Free to use, modify, and distribute.