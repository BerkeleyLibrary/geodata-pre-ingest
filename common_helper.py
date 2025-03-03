import arcpy
import os
from pathlib import Path
import instances
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
    if  any(param.value == instances.no_prcess_path_selected for param in parameters[:n]):
        arcpy.AddError("Error: ❌ no data processing directory was selected from tool 0.1")
        return True
    return False

def output(msg, level='info'):
    logger = workspace_directory.logger
    type = level.lower()   
    if type == 'info':
        val = "✅ " + msg
        logger.info(val)
        arcpy.AddMessage(val)
    elif type == 'error':
        val = "❌ " + msg
        logger.error(val)
        arcpy.AddError(val)
    elif type == 'warning':
        val = "⚠️ " + msg
        logger.warning(val)
        arcpy.AddMessage(val)
    else:
        val = "❌ " + type + msg
        logger.error(val)
        arcpy.AddError(val)




# import os
# os.environ["p_path"] = r"\\napa\mapsshare\yzhou\process_data"
# m = os.getenv("p_path")
# print(m)