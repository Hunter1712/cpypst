import shutil
import os
import hashlib


def copy_file(source, destination):
    try:
        shutil.copy2(source, destination)
        print(f"Copied file: {source} -> {destination}")
        return True
    except (OSError, shutil.Error) as e:
        print(f"Error copying file {source}: {e}")
        return False


def copy_directory(source, destination):
    try:
        shutil.copytree(source, destination)
        print(f"Copied directory: {source} -> {destination}")
        return True
    except (OSError, shutil.Error) as e:
        print(f"Error copying directory {source}: {e}")
        return False


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"Deleted: {file_path}")
        return True
    except OSError as e:
        print(f"Error deleting {file_path}: {e}")
        return False


def calculate_checksum(file_path):
    if not os.path.isfile(file_path):
        return None

    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError as e:
        print(f"Checksum error for {file_path}: {e}")
        return None
