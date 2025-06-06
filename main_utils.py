import os
import time
from file_utils import copy_file, copy_directory, calculate_checksum
from db_utils import create_database_connection, log_operation


def process_item(src, dest, db_name, copied_files, copied_files_lock):
    conn = create_database_connection(db_name)
    if conn is None:
        print(f"DB connection failed for: {src}")
        return

    try:
        if os.path.exists(dest):
            print(f"Skipping (already exists): {src}")
            log_operation(
                conn, src, dest,
                operation="copy",
                status="skipped"
            )
            return

        is_file = os.path.isfile(src)
        is_dir = os.path.isdir(src)
        file_size = os.path.getsize(src) if is_file else None

        attempt = 0
        while attempt < 3:
            attempt += 1

            if is_file:
                success = copy_file(src, dest)
            elif is_dir:
                success = copy_directory(src, dest)
            else:
                print(f"Unknown item type: {src}")
                log_operation(
                    conn, src, dest,
                    operation="skip",
                    status="skipped",
                    file_size=file_size
                )
                return

            if not success:
                log_operation(
                    conn, src, dest,
                    operation="copy",
                    status="failed",
                    error="Copy failed",
                    file_size=file_size
                )
                return

            src_checksum = dest_checksum = None

            if is_file and os.path.isfile(dest):
                src_checksum = calculate_checksum(src)
                dest_checksum = calculate_checksum(dest)

                if src_checksum != dest_checksum:
                    print(f"Checksum mismatch on attempt {attempt}: {src}")
                    log_operation(
                        conn, src, dest,
                        operation="copy",
                        status="failed",
                        error="Checksum mismatch",
                        src_checksum=src_checksum,
                        dest_checksum=dest_checksum,
                        file_size=file_size
                    )
                    try:
                        os.remove(dest)
                    except Exception as e:
                        print(f"Failed to remove mismatched copy: {e}")
                        log_operation(
                            conn, src, dest,
                            operation="cleanup",
                            status="failed",
                            error=str(e)
                        )
                    if attempt < 3:
                        wait_time = 2 ** (attempt - 1)
                        print(f"Retrying {src} in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"Max retries reached for {src}")
                        return
                else:
                    break  # Successful copy with matching checksum
            else:
                break  # Directory copy or no checksum needed

        # Log success
        with copied_files_lock:
            copied_files.append((src, dest))

        log_operation(
            conn, src, dest,
            operation="copy",
            status="success",
            src_checksum=src_checksum,
            dest_checksum=dest_checksum,
            file_size=file_size
        )

    finally:
        try:
            conn.close()
        except Exception as e:
            print(f"DB close error for {src}: {e}")
