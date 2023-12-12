import os
import logging
from pathlib import Path
from shutil import move


################################################################################################
#                             1. functions                                                     #
################################################################################################


def move_files():
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


################################################################################################
#                                 2. setup                                                    #
################################################################################################

# 1. setup log file path
logfile = r"C:\process_data\log\process.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 2. Provide the directory path from which some files have upercase file extension
from_directory_path = r"change me with from_directory_path"

# 3. Provide the destination directory path to which extenstions of all files from 'from_directory_path' and its subdirectories will
# changed to lowercase, then moved
to_directory_path = r"change me with to_directory_path"


################################################################################################
#                            3. Rename file extensions with lower case
# 1. Input "from directory path": some files have uppercase file extension
#    from_directory_path = r"C:\test0"
# 2. Input "to directory path":
#    to_directory_path = r"C:\test1"
# The files from "from_directory_path" and its subdirectories are moved to "to_directory_path" and related subdirectories.
# All files' extentsions should be in lowercase
################################################################################################
def output(msg):
    logging.info(msg)
    print(msg)


def verify_setup(file_paths, directory_paths):
    verified = True
    for file_path in file_paths:
        if not Path(file_path).is_file():
            print(f"File '{file_path}' does not exit.")
            verified = False

    for directory_path in directory_paths:
        if not Path(directory_path).is_dir():
            print(f"Directory '{directory_path}' does not exit.")
            verified = False
    return verified


script_name = "0 - Rename_files_with_lowercase_extension"
output(f"***starting  {script_name}")

if verify_setup(
    [],
    [
        from_directory_path,
        to_directory_path,
    ],
):
    move_files()
    output(f"***completed {script_name}")
