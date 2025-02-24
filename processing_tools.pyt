# -*- coding: utf-8 -*-

import arcpy
import os
import logging
from pathlib import Path
from datetime import datetime
from shutil import copyfile, rmtree
import util
import workspace_directory
import common_helper
import prepare_batch


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GeoblacklightToolbox"
        self.alias = "geoblacklight_toolbox"    
        self.tools = [CreateWorkspaceTool, SelectWorkspaceTool, PrepareBatchTool]

class CreateWorkspaceTool:
    def __init__(self):
        self.label = "0 - Create workspace template directory"
        self.title = "This is a title"
        self.description = "0 - Create a template processing workspace "

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

        return

class SelectWorkspaceTool:
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

   

class PrepareBatchTool:
    def __init__(self):
        self.label = "1 .1 - prepare_batch"
        self.description = "1 .1 - prepare_batch - desc"

    def getParameterInfo(self):
        from_source_path_param = arcpy.Parameter(
            displayName="Projected from below source batch directory",
            name="From Directory",
            datatype="GPString",
            direction="Output"
        )    
        to_projected_path_param = arcpy.Parameter(
            displayName="To this directory",
            name="To Directory",
            datatype="GPString",
            direction="Output"

        )
        
        return [ from_source_path_param, to_projected_path_param]

    def updateParameters(self, parameters):
        val = "Please select a geodata batch in tool 0. 0 - Select a processing batch"
        val1 = val
        val2 = val
        if (workspace_directory.projected_batch_directory_path is not None):
            val1 = workspace_directory.source_batch_directory_path
            val2 = workspace_directory.projected_batch_directory_path            
        parameters[0].value = val1
        parameters[1].value = val2
        return

    def execute(self, parameters, messages):
        arcpy.AddMessage("!!- starting preparing data!!!.")
        logfile = r"C:\process_data\log\process.log"
        logging.basicConfig(
            filename=logfile,
            level=logging.INFO,
            format="%(message)s - %(asctime)s - %(funcName)s - %(levelname)s",
        )

        # input_fc = parameters[0].valueAsText
        # output_fc = parameters[1].valueAsText

        # source_batch_directory_path =  common_helper.batch_directory
        source_batch_directory_path = workspace_directory.source_batch_directory_path
        # 3. Please provide projected data directory path
        # parent_path = os.path.dirname(source_batch_directory_path)
        # projected_batch_directory_path = fr"{parent_path}\source_batch_projected"
        projected_batch_directory_path = workspace_directory.projected_batch_directory_path

       
        arcpy.AddMessage(source_batch_directory_path)

        arcpy.AddMessage(projected_batch_directory_path)

        # 4. A GeoTIFF projected file
        geotif_referenced_filepath = (
            r"C:\pre-ingestion-config\projected_raster\5048_1_reproject4326.tif"
        )

        
        if common_helper.verify_setup(
            [geotif_referenced_filepath],
            [source_batch_directory_path, projected_batch_directory_path],
        ):
            source_batch = prepare_batch.SourceBatch(source_batch_directory_path, logging)
            source_batch.check_files()
            source_batch.prepare(projected_batch_directory_path, geotif_referenced_filepath)
        script_name = "1 .1 - prepare_batch.py"
        arcpy.AddMessage(f"***completed1 {script_name}")
        return

    
