import os
import time
from file_utils import (
    copy_file,
    copy_directory,
    delete_file,
    calculate_checksum,
)
from db_utils import log_operation, check_file_status


def process_item(src, dest, conn, copied_items):
    """
    Process copying of a single item with retry, logging, and checksum comparison.
    """
    cursor = conn.cursor()

    # Check DB status
    status = check_file_status(cursor, src)
    if status == "success" and os.path.exists(dest):
        # Re-verify checksums in case of source changes
        src_checksum = calculate_checksum(src)
        dest_checksum = calculate_checksum(dest)
        if src_checksum == dest_checksum:
            print(f"Skipping already copied: {src}")
            copied_items.append((src, dest))
            return True
        else:
            print(f"Checksum mismatch for {src}, re-copying...")

    retry_count = 3
    for attempt in range(retry_count):
        try:
            if os.path.isfile(src):
                copy_success = copy_file(src, dest)
                operation_type = "copy"
            elif os.path.isdir(src):
                copy_success = copy_directory(src, dest)
                operation_type = "copy"
            else:
                print(f"Skipping: {src} (not a file or directory)")
                log_operation(cursor, src, dest, "skip", "skipped")
                return False

            if copy_success:
                src_checksum = calculate_checksum(src)
                dest_checksum = calculate_checksum(dest)

                if src_checksum == dest_checksum:
                    copied_items.append((src, dest))
                    log_operation(cursor, src, dest, operation_type, "success")
                    print(f"Copied file: {src} → {dest}")
                    return True
                else:
                    log_operation(cursor, src, dest, operation_type,
                                  "failed", "Checksum mismatch")
                    print(
                        f"Checksum mismatch after copying {src}. Retrying...")
                    if os.path.exists(dest):
                        os.remove(dest)
            else:
                log_operation(cursor, src, dest, operation_type,
                              "failed", "Copy failed")
        except Exception as e:
            log_operation(cursor, src, dest, "copy", "failed", str(e))
            print(f"Unexpected error while copying {src}: {e}")

        if attempt < retry_count - 1:
            wait = 2 ** attempt
            print(f"Retrying in {wait} seconds...")
            time.sleep(wait)
        else:
            print(f"Failed to copy {src} after {retry_count} attempts.")

    return False
