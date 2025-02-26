# -*- coding: utf-8 -*-

import arcpy
import logger
import workspace_directory
import common_helper
import batch_export_csv

class ExportCsvTool(object):
    def __init__(self):
        self.label = "2 - Export geodata metadata to a CSV file"

    def getParameterInfo(self):
 
        from_soure_batch_param = arcpy.Parameter(
            displayName="From source batch directory",
            name="from_soure_batch",
            datatype="GPString",
            direction="Output"
        )

        to_csv_file_param = arcpy.Parameter(
            displayName="Creating a csv file to this directory",
            name="csv_file_path",
            datatype="GPString",
            direction="Output"
        )
        
        return [from_soure_batch_param, to_csv_file_param]

    def updateParameters(self, parameters):
        val = "Please select a geodata batch in tool 0. 0 - Select a processing batch"
        val1 = val
        val2 = val
        if (workspace_directory.source_batch_directory_path is not None):
            val1 = workspace_directory.source_batch_directory_path
            val2 = workspace_directory.csv_files_directory_path            
        parameters[0].value = val1
        parameters[1].value = val2
        return

    def execute(self, parameters, messages):
        source_batch_directory_path = workspace_directory.source_batch_directory_path
        csv_files_directory_path = workspace_directory.csv_files_directory_path   
        

        if common_helper.verify_setup(
            [],
            [source_batch_directory_path, csv_files_directory_path],
        ):
            all_geofile_paths = batch_export_csv.geofile_paths()
            batch_export_csv.export_main_csv(all_geofile_paths)
            batch_export_csv.export_resp_csv(all_geofile_paths)
        return

    
