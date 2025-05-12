import os
import shutil
import hashlib


def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError as e:
        print(f"Error creating directory {path}: {e}")
        return False


def copy_file(src, dest):
    try:
        shutil.copy2(src, dest)
        print(f"Copied file: {src} → {dest}")
        return True
    except Exception as e:
        print(f"Error copying file {src}: {e}")
        return False


def copy_directory(src, dest):
    try:
        shutil.copytree(src, dest, dirs_exist_ok=True)
        print(f"Copied directory: {src} → {dest}")
        return True
    except Exception as e:
        print(f"Error copying directory {src}: {e}")
        return False


def delete_file(path):
    try:
        os.remove(path)
        print(f"Deleted: {path}")
        return True
    except Exception as e:
        print(f"Error deleting file {path}: {e}")
        return False


def calculate_checksum(file_path):
    if not os.path.isfile(file_path):
        return None

    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error calculating checksum for {file_path}: {e}")
        return None
