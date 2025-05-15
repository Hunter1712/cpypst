# cpypst

## Automated File Copying and Deletion

A simple multithreaded tool that copies files or folders, verifies them using checksums, logs all operations into an SQLite database, and deletes the original files after successful copying. Designed for ease of use with no external dependencies.

## Features

- Copies files or entire directories
- Verifies integrity using SHA-256 checksums
- Retries failed copies up to 3 times
- Deletes original files after successful copy and verification
- Logs all actions (success, failure, skip, etc.) to an SQLite database
- Thread-safe database access
- Clean and modular Python code

## How It Works

1. A database is created if it doesn't already exist.
2. For each file or directory:
   - It checks if the destination already exists.
   - If not, it attempts to copy the item.
   - If the item is a file, it calculates and compares SHA-256 checksums.
   - On checksum mismatch, it retries up to 3 times.
   - If the copy is successful and the checksum matches (for files), the original is deleted.
   - Every action is logged in the database.

## File Structure

- **db_utils.py** – Manages database connections and logs operations
- **file_utils.py** – Handles copying, deleting, and checksumming
- **main_utils.py** – Coordinates processing logic, retries, and logging

## Requirements

- Python 3.8 or newer
- Uses only standard Python libraries:
  - `os`, `shutil`, `sqlite3`, `hashlib`, `threading`, `time`

## Database Log Format

Each entry in the `file_operations` table includes:

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
