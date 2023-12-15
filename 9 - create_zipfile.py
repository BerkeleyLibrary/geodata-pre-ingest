import os
import logging
from pathlib import Path
import zipfile

################################################################################################
#                             1. functions                                                     #
################################################################################################


def zip_directories():
    source_dirs = source_directores()
    final_zipfile = os.path.join(result_directory_path, zipfile_name)
    with zipfile.ZipFile(final_zipfile, "w", zipfile.ZIP_DEFLATED) as zipf:
        for source_dir in source_dirs:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    destname = os.path.relpath(file_path, result_directory_path)
                    zipfile_basename = os.path.splitext(zipfile_name)[0]
                    dest_rel_path = os.path.join(zipfile_basename, destname)
                    zipf.write(file_path, dest_rel_path)


# Below two directores are the output directories from script 7
def source_directores():
    dirs = []
    ingestion_file_dirpath = os.path.join(result_directory_path, "ingestion_files")
    collection_ingestion_file_dirpath = os.path.join(
        result_directory_path, "ingestion_collection_files"
    )
    if has_subdirectories_files(ingestion_file_dirpath):
        dirs.append(ingestion_file_dirpath)
    if has_subdirectories_files(collection_ingestion_file_dirpath):
        dirs.append(collection_ingestion_file_dirpath)

    check_ingestion_directory(dirs)
    return dirs


def check_ingestion_directory(source_dirs):
    if not bool(source_dirs):
        txt = f"No ingestion directories or files found under {result_directory_path}, have you run script 7 to create ingestion files?"
        log_raise_error(txt)


def has_subdirectories_files(directory):
    if os.path.isdir(directory):
        return any(os.scandir(directory))
    return False


def log_raise_error(text):
    logging.info(text)
    raise ValueError(text)


################################################################################################
#                                 2. setup
#  Giving a unique zipfile_name before running this script                                                #
################################################################################################

# 1. setup log file path
logfile = r"C:\process_data\log\process.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 2. please provide result directory path
result_directory_path = r"C:\process_data\results"

# 3. batchname
zipfile_name = "give_me_a_unique_name.zip"


################################################################################################
#                3. Create a final ingestion zipfile for Gingr - the ingestion tool
################################################################################################
def output(msg):
    logging.info(msg)
    print(msg)


def verify_setup(file_paths, directory_paths):
    if zipfile_name == "give_me_a_unique_name.zip":
        txt = "Zipfile name is 'give_me_a_unique_name.zip', Please give a unique name before running script 9."
        raise ValueError(txt)

    verified = True
    for file_path in file_paths:
        if not Path(file_path).is_file():
            print(f"{file_path} does not exit.")
            verified = False

    for directory_path in directory_paths:
        if not Path(directory_path).is_dir():
            print(f"{directory_path} does not exit.")
            verified = False
    return verified


script_name = "9 - create_zipfile.py"
output(f"***starting  {script_name}")

if verify_setup(
    [],
    [result_directory_path],
):
    zip_directories()
    output_msg = f"***completed {script_name}, \n please find the final ingestion zipfile at: {os.path.join(result_directory_path, zipfile_name)}"
    output(output_msg)
