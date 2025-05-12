# file_utils.py
import shutil
import os
import hashlib


def copy_file(source_item_path, destination_item_path):
    try:
        shutil.copy2(source_item_path, destination_item_path)
        print(f"Copied: {source_item_path} to {destination_item_path}")
        return True
    except (OSError, shutil.Error) as e:
        print(f"Error copying file {source_item_path}: {e}")
        return False


def copy_directory(source_item_path, destination_item_path):
    try:
        shutil.copytree(source_item_path, destination_item_path)
        print(
            f"Copied directory: {source_item_path} to {destination_item_path}")
        return True
    except (OSError, shutil.Error) as e:
        print(f"Error copying directory {source_item_path}: {e}")
        return False


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
        return True
    except OSError as e:
        print(f"Error deleting file {file_path}: {e}")
        return False


def calculate_checksum(file_path):
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
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
