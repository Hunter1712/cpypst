import os
from db_utils import create_database_connection, create_database_table
from file_utils import create_directory, delete_file
from main_utils import process_item


def main():
    source_folder = "source_folder"
    destination_folder = "destination_folder"
    db_name = "file_operations.db"

    create_directory(source_folder)
    create_directory(destination_folder)

    # Create dummy files
    for i in range(3):
        with open(os.path.join(source_folder, f"file{i}.txt"), "w") as f:
            f.write(f"This is dummy file {i}.")

    conn = create_database_connection(db_name)
    if not conn:
        return

    create_database_table(conn)

    copied_items = []
    for item in os.listdir(source_folder):
        src = os.path.join(source_folder, item)
        dest = os.path.join(destination_folder, item)

        if os.path.isfile(src):
            if process_item(src, dest, conn, copied_items):
                print(f"Copied: {src}")
            else:
                print(f"Failed to copy: {src}")

    # Delete copied source files
    for src, _ in copied_items:
        if os.path.isfile(src):
            delete_file(src)

    conn.close()


if __name__ == "__main__":
    main()
