import arcpy
from pathlib import Path
import importlib
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

# def not_selected(parameters, n):
#     if  any(param.value == constants.no_prcess_path_selected for param in parameters[:n]):
#         return True
#     return False

def verify_selected_source_batch_directory(parameters, n):
    if any(param.value == constants.no_prcess_path_selected for param in parameters[:n]):
        arcpy.AddError("Error: ❌ no data processing directory was selected from tool 0.1, please select one")
        raise arcpy.ExecuteError
    return
   
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

def directories_existed(directory_paths):
    exist = True
    for directory_path in directory_paths:
        if not Path(directory_path).is_dir():
            msg = f"{directory_path} does not exit."
            exist = False
    return exist
# def csv_arkid_filepath(directory_path, name):
#     return fr"{directory_path }\{name}_arkid.csv"

def csv_filepath(name, has_arkid=False):
    if has_arkid:
        return fr"{workspace_directory.csv_files_arkid_directory_path}\{name}_arkid.csv"
    else:
        return fr"{workspace_directory.csv_files_directory_path }\{name}.csv"

def log_raise_error(msg):
    output(msg, 1)
    raise ValueError(msg)

def paths_exist(paths, is_file=True):
    all_exist = True
    for path in paths:
        path_obj = Path(path)
        if (is_file and not path_obj.is_file()) or (not is_file and not path_obj.is_dir()):
            msg = f"{path} does not exist."
            output(msg, 1)
            all_exist = False
    return all_exist


def workspace_directories_exist():
    directory_paths = [workspace_directory.process_directory_path, 
                       workspace_directory.source_batch_directory_path, 
                       workspace_directory.process_directory_path,
                       workspace_directory.csv_files_directory_path,
                       workspace_directory.projected_batch_directory_path,
                       workspace_directory.results_directory_path,
                       workspace_directory.log_directory_path]
    return paths_exist(directory_paths, False)

def verify_workspace_and_files(file_paths):
    all_files_exist = paths_exist(file_paths)
    all_directories_exist =  workspace_directories_exist()
    if not (all_files_exist and all_directories_exist):
        raise ValueError(fr"Missing workspace direcotories and CSV files, please see the log file '{workspace_directory.log_directory_path}/process.txt' for details")



def call_run(module_name):
    try:
        output(fr"*** Starting to run tool_{module_name}.")
        module = importlib.import_module(module_name)
        if hasattr(module, 'run_tool'):
            module.run_tool()
            output(fr"*** Completed to run tool_{module_name}.")
        else:
            output(f"{module_name}.py does not have a 'run_tool' method.", 2)
    except ModuleNotFoundError:
        output(f"Module {module_name} not found.", 2)
        raise
    except Exception as e:
        arcpy.AddError(f"An error occurred while executing tool_{module_name}.")
        raise




# import os
# os.environ["p_path"] = r"\\napa\mapsshare\yzhou\process_data"
# m = os.getenv("p_path")
# print(m)