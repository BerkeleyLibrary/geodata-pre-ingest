import arcpy
import os
import logging
from typing import List
from pathlib import Path
from datetime import datetime


################################################################################################
#                             1. functions                                                        #
################################################################################################


def add_pyramid_to_geotif_files():
    geofiles = get_filepaths(projected_batch_directory_path, ".tif")
    for geofile in geofiles:
        pyramid(geofile)


def get_filepaths(directory, ext):
    paths = []
    for file in os.listdir(directory):
        if file.endswith(ext):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                paths.append(file_path)
    return paths


def pyramid(filepath):
    pylevel = "7"
    skipfirst = "NONE"
    resample = "NEAREST"
    compress = "Default"
    quality = "70"
    skipexist = "SKIP_EXISTING"
    try:
        arcpy.management.BuildPyramids(
            filepath, pylevel, skipfirst, resample, compress, quality, skipexist
        )
    except Exception as ex:
        logging.info(f"{filepath} - {ex}")


################################################################################################
#                                 2. set up                                                    #
################################################################################################

# 1. Please provide your local log file path
logfile = r"C:\process_data\log\process.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s - %(funcName)s - %(levelname)s",
)

# 2. Please provide projected data directory path
projected_batch_directory_path = r"C:\process_data\source_batch_projected"


################################################################################################
#                                3. Run options                                                #
################################################################################################
def output(msg):
    logging.info(msg)
    print(msg)


def verify_setup(file_paths, directory_paths):
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


script_name = "1 .2 - raster_pyramid_batch.py"
output(f"***starting  {script_name}")

if verify_setup(
    [],
    [projected_batch_directory_path],
):
    add_pyramid_to_geotif_files()
    output(f"***completed {script_name}")
