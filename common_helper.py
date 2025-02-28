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

def stop_execute(parameters, n):
    return any(param.value == instances.no_prcess_path_selected for param in parameters[:n])

def output(msg, is_error=False):
    logger = workspace_directory.logger
    if is_error:
        val = "❌ " + msg
        logger.error(val)
        arcpy.AddError(val)
    else:
        val = "✅ " + msg
        logger.info(val)
        arcpy.AddMessage(val)

# def the_path(batch_path):
#     parent_path = os.path.dirname(batch_path)
#     path1 = fr"{parent_path}\source_batch_projected"
#     return path1




# import os
# os.environ["p_path"] = r"\\napa\mapsshare\yzhou\process_data"
# m = os.getenv("p_path")
# print(m)