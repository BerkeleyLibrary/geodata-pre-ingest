import arcpy
import the_logger
import workspace_directory

class SelectWorkspaceTool(object):
    def __init__(self):
        self.label = "0 .2 - Select a data processing directory"
        self.description = "0.0 - "

    def getParameterInfo(self):
        workespace_name_param = arcpy.Parameter(
            displayName="Geobalcklight data processing directory",
            name="Input Processing Pirectory",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
       
        return [workespace_name_param]
   
    def execute(self, parameters, messages):
        parent_path= parameters[0].valueAsText
        workspace_directory.process_directory_path = parent_path
        workspace_directory.source_batch_directory_path = fr"{parent_path}\source_batch"
        workspace_directory.projected_batch_directory_path = fr"{parent_path}\source_batch_projected"     
        workspace_directory.csv_files_directory_path = fr"{parent_path}\csv_files"
        workspace_directory.csv_files_arkid_directory_path = fr"{parent_path}\csv_files_arkid"
        workspace_directory.results_directory_path = fr"{parent_path}\results"
        workspace_directory.log_directory_path = fr"{parent_path}\log"
        workspace_directory.logger = the_logger.setup_logger(workspace_directory.log_directory_path)
        arcpy.AddMessage(f"✅ Data processing directory is selected: {parent_path}")
        return

   
