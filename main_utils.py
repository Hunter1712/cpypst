# main_utils.py
import os
import time
from file_utils import copy_file, copy_directory, calculate_checksum
from db_utils import create_database_connection, log_operation


def process_item(src, dest, db_name, copied_files, copied_files_lock):
    conn = create_database_connection(db_name)
    if conn is None:
        print(f"Failed DB connection for: {src}")
        return

    try:
        if os.path.exists(dest):
            print(f"Skipping: {src} (already exists in destination)")
            log_operation(conn, src, dest, "copy", "skipped")
            with copied_files_lock:
                copied_files.append((src, dest))
            return

        retry_count = 3
        for attempt in range(retry_count):
            try:
                copy_success = False
                operation_type = "copy"

                if os.path.isfile(src):
                    copy_success = copy_file(src, dest)
                elif os.path.isdir(src):
                    copy_success = copy_directory(src, dest)
                else:
                    print(f"Skipping: {src} (not a file or directory)")
                    log_operation(conn, src, dest, "skip", "skipped")
                    return

                if copy_success:
                    if os.path.isfile(src) and os.path.isfile(dest):
                        source_checksum = calculate_checksum(src)
                        dest_checksum = calculate_checksum(dest)

                        if source_checksum == dest_checksum:
                            with copied_files_lock:
                                copied_files.append((src, dest))
                            log_operation(conn, src, dest,
                                          operation_type, "success")
                            return
                        else:
                            log_operation(
                                conn, src, dest, operation_type, "failed", "Checksum mismatch")
                            os.remove(dest)
                            print(f"Checksum mismatch for {src}")
                    else:
                        with copied_files_lock:
                            copied_files.append((src, dest))
                        log_operation(conn, src, dest,
                                      operation_type, "success")
                        return
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
    finally:
        conn.close()
