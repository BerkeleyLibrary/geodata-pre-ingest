import arcpy
from pathlib import Path
import importlib
import os
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

def verify_workspace_and_files(file_paths=[]):
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


GEOFILE_EMPTY = "empty"  # no geofile value: metadata-only (collection) row
GEOFILE_EXISTS = "exists"  # geofile value is an existing file
GEOFILE_MISSING = "missing"  # geofile value is set but file does not exist


def geofile_status(row):
    geofile_path = (row.get("geofile") or "").strip()
    if not geofile_path:
        return GEOFILE_EMPTY, geofile_path
    if os.path.isfile(geofile_path):
        return GEOFILE_EXISTS, geofile_path
    return GEOFILE_MISSING, geofile_path


def has_dataset(row):
    status, geofile_path = geofile_status(row)
    if status == GEOFILE_MISSING:
        log_raise_error(
            f"Please check the main csv file: geofile '{geofile_path}' does not exist "
            f"(arkid: {row.get('arkid')})"
        )
    return status == GEOFILE_EXISTS


def require_arkid(row):
    arkid = (row.get("arkid") or "").strip()
    if not arkid:
        log_raise_error(
            f"Please check the main csv file: missing arkid in {row.get('geofile')}"
        )
    return arkid


def has_arkid_dataset(row):
    require_arkid(row)
    return has_dataset(row)

def required_geoblacklight(metadata_path):
    geoblacklight_path = os.path.join(metadata_path, "geoblacklight.json")
    if not Path(geoblacklight_path).is_file():
        log_raise_error(f"missing file: {geoblacklight_path}")
