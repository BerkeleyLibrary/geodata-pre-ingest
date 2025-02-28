import workspace_directory
import arcpy


def setup_workspace(parent_path):
     workspace_directory.source_batch_directory_path = fr"{parent_path}\source_batch"
     workspace_directory.projected_batch_directory_path = fr"{parent_path}\source_batch_projected"     
     workspace_directory.csv_files_directory_path = fr"{parent_path}\csv_files"
     workspace_directory.csv_files_arkid_directory_path = fr"{parent_path}\csv_files_arkid"
     workspace_directory.results_directory_path = fr"{parent_path}\results"
     workspace_directory.log_directory_path = fr"{parent_path}\log"


def output(logger, msg, is_error=False):
    if is_error:
        logger.error(msg)
        arcpy.AddError(msg)
    else:
        logger.info(msg)
        arcpy.AddMessage(msg)