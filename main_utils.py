import os
import time
import threading
from file_utils import copy_file, copy_directory, delete_file, calculate_checksum
from db_utils import log_operation

# Shared lock to be used for DB access
db_lock = threading.Lock()


def process_item(src, dest, conn, copied_files):
    """
    Handles the copying of a single item (file or directory) with retries
    and logging. Uses DB lock to ensure thread safety.
    """
    with db_lock:
        cursor = conn.cursor()

    # Check if the destination file exists
    if os.path.exists(dest):
        print(f"Skipping: {src} (already exists in destination)")
        log_operation(conn, src, dest, "copy", "skipped")
        copied_files.append((src, dest))
        return True

    # Retry logic for copying the file/directory
    retry_count = 3
    for attempt in range(retry_count):
        try:
            copy_success = False
            if os.path.isfile(src):
                copy_success = copy_file(src, dest)
                operation_type = "copy"
            elif os.path.isdir(src):
                copy_success = copy_directory(src, dest)
                operation_type = "copy"
            else:
                print(f"Skipping: {src} (not a file or directory)")
                log_operation(conn, src, dest, "skip", "skipped")
                return False

            if copy_success:
                source_checksum = calculate_checksum(src)
                dest_checksum = calculate_checksum(dest)

                if source_checksum == dest_checksum:
                    copied_files.append((src, dest))
                    log_operation(conn, src, dest, operation_type, "success")
                    return True
                else:
                    log_operation(conn, src, dest, operation_type,
                                  "failed", "Checksum mismatch")
                    # Delete the corrupted copy if checksums do not match
                    os.remove(dest)
                    print(f"Checksum mismatch for {src}")
        except Exception as e:
            log_operation(conn, src, dest, "copy", "failed", str(e))
            print(f"Error processing {src}: {e}")

        if attempt < retry_count - 1:
            wait_time = 2 ** attempt
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(f"Failed to copy {src} after {retry_count} attempts.")
            log_operation(conn, src, dest, "copy",
                          "failed", "Retry limit reached")
            return False

    return False
