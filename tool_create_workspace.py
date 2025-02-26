# -*- coding: utf-8 -*-

import arcpy
import os
import logger

class CreateWorkspaceTool(object):
    def __init__(self):
        self.label = "0 .0 - Create workspace template directory"

    def getParameterInfo(self):
        dir_path_param = arcpy.Parameter(
            displayName="Select a directory",
            name="Input Processing directory path",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        workspace_name_param = arcpy.Parameter(
            displayName="Input a workspace name",
            name="Input Processing directory name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        
        return [ dir_path_param,  workspace_name_param]

    def execute(self, parameters, messages):
        process_dir =  parameters[0].valueAsText
        process_worksapce = os.path.join(process_dir, parameters[1].valueAsText )
        os.makedirs(process_worksapce, exist_ok=True)

        sub_dir_names = ["csv_files", "csv_files_arkid", "results", "source_batch","log","source_batch_projected"]
        for name in sub_dir_names:
            path = os.path.join(process_worksapce, name)
            os.makedirs(path, exist_ok=True)
        logger.output("workspace created!!")
        return