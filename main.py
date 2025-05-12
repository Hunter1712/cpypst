import os
import threading
from db_utils import create_database_connection, create_database_table
from file_utils import delete_file
from main_utils import process_item


def main():
    """
    Main function to orchestrate the file copy, delete, and logging process.
    """

    source_folder = "source_folder"
    destination_folder = "destination_folder"
    db_name = "file_operations.db"

    os.makedirs(source_folder, exist_ok=True)
    for i in range(3):
        with open(os.path.join(source_folder, f"file{i}.txt"), "w") as f:
            f.write(f"This is dummy file {i}.")

    # Create and initialize the database connection and table
    conn = create_database_connection(db_name)
    if conn is None:
        return

    create_database_table(conn)

    copied_items = []

    # Ensure the destination folder exists
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder, exist_ok=True)

    # List files in the source folder and start processing them
    threads = []
    for item in os.listdir(source_folder):
        source_item_path = os.path.join(source_folder, item)
        destination_item_path = os.path.join(destination_folder, item)

        # Create a new thread for each item copy operation
        thread = threading.Thread(target=process_item, args=(
            source_item_path, destination_item_path, conn, copied_items))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Delete files that were successfully copied
    if copied_items:
        deleted_files_count = 0
        for src, _ in copied_items:
            if os.path.isfile(src):
                if delete_file(src):
                    deleted_files_count += 1

        print(f"{deleted_files_count} files deleted successfully.")
    else:
        print("No files were copied, so none were deleted.")

    conn.close()


if __name__ == "__main__":
    main()
