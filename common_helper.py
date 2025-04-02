import arcpy
from pathlib import Path
import importlib
import workspace_directory
   
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

def call_run_tool(module_name):
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

def assign_parameters(parameters, values):
    for i, val in enumerate(values):
        parameters[i].value = val