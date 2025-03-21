import arcpy
from pathlib import Path
import constants
import workspace_directory

#1. mapsshare:  \\napa\mapsshare\yzhou\process_data\source_batch


# batch_directory = fr"\\napa\mapsshare\yzhou\process_data\source_batch"
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

def no_processing_directory_selected(parameters, n):
    if  any(param.value == constants.no_prcess_path_selected for param in parameters[:n]):
        arcpy.AddError("Error: ❌ no data processing directory was selected from tool 0.1")
        return True
    return False

def output(msg, level=0):
    logger = workspace_directory.logger
     
    if level == 0: #'info'
        val = "✅ " + msg
        logger.info(val)
        arcpy.AddMessage(val)
    elif level == 1: #'warning'
        val = "⚠️ " + msg
        logger.warning(val)
        arcpy.AddMessage(val)
    elif level == 2: #'error'
        val = "❌ " + msg
        logger.error(val)
        arcpy.AddError(val)
    else:
        val = "❌ " + "incorrect log level - " + msg
        logger.error(val)
        arcpy.AddError(val)


def files_existed(file_paths):
    file_existed = True
    for file_path in file_paths:
        if not Path(file_path).is_file():
            msg = f"{file_path} does not exit."
            output(msg, 1)
            file_existed  = False
    return  file_existed 


# import os
# os.environ["p_path"] = r"\\napa\mapsshare\yzhou\process_data"
# m = os.getenv("p_path")
# print(m)