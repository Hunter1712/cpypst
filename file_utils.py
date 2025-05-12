import shutil
import os
import hashlib


def create_destination_directory(destination_folder):
    """Creates the destination directory if it does not exist."""
    try:
        os.makedirs(destination_folder, exist_ok=True)
        return True
    except OSError as e:
        print(f"Error creating destination folder: {e}")
        return False


def check_source_directory(source_folder):
    """Checks if the source directory exists."""
    if not os.path.exists(source_folder):
        print(f"Source folder '{source_folder}' does not exist.")
        return False
    return True


def copy_file(source_item_path, destination_item_path):
    """Copies a single file from source to destination."""
    try:
        shutil.copy2(source_item_path, destination_item_path)
        print(f"Copied: {source_item_path} to {destination_item_path}")
        return True
    except (OSError, shutil.Error) as e:
        print(f"Error copying file {source_item_path}: {e}")
        return False


def copy_directory(source_item_path, destination_item_path):
    """Copies a directory from source to destination"""
    try:
        shutil.copytree(source_item_path, destination_item_path)
        print(
            f"Copied directory: {source_item_path} to {destination_item_path}")
        return True
    except (OSError, shutil.Error) as e:
        print(f"Error copying directory {source_item_path}: {e}")
        return False


def delete_file(file_path):
    """Deletes a single file."""
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
        return True
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")
        return False


def calculate_checksum(file_path):
    """Calculates the SHA-256 checksum of a file."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as file:
            buffer = file.read(65536)
            while buffer:
                hasher.update(buffer)
                buffer = file.read(65536)
    except OSError as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    return hasher.hexdigest()
