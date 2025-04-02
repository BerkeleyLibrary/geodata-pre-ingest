import os
# from pathlib import Path
from shutil import move

# Move batch files and rename extentions with lower cases
def run_tool(from_directory_path, to_directory_path):
    for root, _, files in os.walk(from_directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                temp_file = lowercase_extension(file)
                temp_file_path = os.path.join(root, temp_file)
                rel_name = os.path.relpath(temp_file_path, from_directory_path)
                dest_file_path = os.path.join(to_directory_path, rel_name)
                os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)
                move(file_path, dest_file_path)


def lowercase_extension(filename):
    parts = filename.split(".")
    modified_parts = [part.lower() if i > 0 else part for i, part in enumerate(parts)]
    return ".".join(modified_parts)
