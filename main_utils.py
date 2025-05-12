# main_utils.py
import os
import time
from file_utils import (
    copy_file,
    copy_directory,
    delete_file,
    calculate_checksum,
)
from db_utils import log_operation, check_file_status


def _process_copy_item(
    source_item_path, destination_item_path, conn, copied_files
):
    """
    Handles the copying of a single item (file or directory) with retries
    and logging.
    """

    cursor = conn.cursor()

    if os.path.exists(destination_item_path):
        status = check_file_status(cursor, source_item_path)
        if status == "success":
            print(
                f"  Skipping: {source_item_path} (already copied successfully)")
            copied_files.append((source_item_path, destination_item_path))
            return True

    retry_count = 3
    for attempt in range(retry_count):
        try:
            if os.path.isfile(source_item_path):
                copy_success = copy_file(
                    source_item_path, destination_item_path)
                operation_type = "copy"
            elif os.path.isdir(source_item_path):
                copy_success = copy_directory(
                    source_item_path, destination_item_path
                )
                operation_type = "copy"
            else:
                print(
                    f"  Skipping: {source_item_path} (not a file or directory)")
                log_operation(
                    cursor,
                    source_item_path,
                    destination_item_path,
                    "skip",
                    status="skipped",
                )
                return False

            if copy_success:
                source_checksum = calculate_checksum(source_item_path)
                dest_checksum = calculate_checksum(destination_item_path)
                if source_checksum == dest_checksum:
                    copied_files.append(
                        (source_item_path, destination_item_path))
                    log_operation(
                        cursor,
                        source_item_path,
                        destination_item_path,
                        operation_type,
                        status="success",
                    )
                    return True
                else:
                    log_operation(
                        cursor,
                        source_item_path,
                        destination_item_path,
                        operation_type,
                        error="Checksum mismatch",
                        status="failed",
                    )
                    print("  Checksums do not match!")
                    if os.path.exists(destination_item_path):
                        os.remove(destination_item_path)
            else:
                log_operation(
                    cursor,
                    source_item_path,
                    destination_item_path,
                    operation_type,
                    error="Failed to copy",
                    status="failed",
                )

        except Exception as e:
            log_operation(
                cursor,
                source_item_path,
                destination_item_path,
                operation_type,
                error=str(e),
                status="failed",
            )
            print(f"  An unexpected error occurred: {e}")

        if attempt < retry_count - 1:
            wait_time = 2**attempt
            print(f"  Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print(
                f"  Failed to copy {source_item_path} after {retry_count} attempts."
            )
            return False
    return False
