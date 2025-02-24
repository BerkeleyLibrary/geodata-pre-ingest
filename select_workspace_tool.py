# -*- coding: utf-8 -*-
import arcpy
# import util
import workspace_directory

class SelectWorkspaceTool(object):
    def __init__(self):
        self.label = "0. 0 - Select a processing batch"
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
        # util.setup_workspace(parent_path)
        workspace_directory.source_batch_directory_path = fr"{parent_path}\source_batch"
        workspace_directory.projected_batch_directory_path = fr"{parent_path}\source_batch_projected"     
        workspace_directory.csv_files_directory_path = fr"{parent_path}\csv_files"
        workspace_directory.csv_files_arkid_directory_path = fr"{parent_path}\csv_files_arkid"
        workspace_directory.results_directory_path = fr"{parent_path}\results"
        workspace_directory.log_directory_path = fr"{parent_path}\log"
        return

   
