import arcpy
import os

class CreateWorkspaceTool(object):
    def __init__(self):
        self.label = "0 .0 - Create a new data processing directory with workspace template"

    def getParameterInfo(self):
        dir_path_param = arcpy.Parameter(
            displayName="Select a directory",
            name="Input Processing directory path",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        workspace_name_param = arcpy.Parameter(
            displayName="Input a data processing directory name",
            name="Input Processing directory name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        
        return [ dir_path_param,  workspace_name_param]

    def execute(self, parameters, messages):

        workspace_directory =  parameters[0].valueAsText
        workspace_name = os.path.join(workspace_directory, parameters[1].valueAsText )

        arcpy.AddMessage(f"✅ *** Starting to create data processing directory and sub-directories at {workspace_directory}")
        os.makedirs(workspace_name, exist_ok=True)

        sub_dir_names = ["csv_files", "csv_files_arkid", "results", "source_batch","log","source_batch_projected"]
        for dir_name in sub_dir_names:
            path = os.path.join(workspace_name, dir_name)
            os.makedirs(path, exist_ok=True)
        arcpy.AddMessage(f"✅ *** Data processing directory and sub-directories have been created at {workspace_directory}")
        return