
import arcpy
import common_helper
import workspace_directory
import batch_export_csv
import instances

class BatchExportCsvTool(object):
    def __init__(self):
        self.label = "2 - Run to export metadata to a CSV file"

    def getParameterInfo(self):
        from_source_path_param = arcpy.Parameter(
            displayName="From below source batch directory",
            name="From Directory",
            datatype="GPString",
            direction="Output"
        )    
        to_csv_path_param = arcpy.Parameter(
            displayName="To this directory",
            name="To Directory",
            datatype="GPString",
            direction="Output"

        )
        
        return [ from_source_path_param, to_csv_path_param]

    def updateParameters(self, parameters):
        val0 = instances.no_prcess_path_selected
        val1 = val0
        if (workspace_directory.source_batch_directory_path is not None):
            val0 = workspace_directory.source_batch_directory_path
            val1 = workspace_directory.csv_files_directory_path           
        parameters[0].value = val0
        parameters[1].value = val1
        return

    def execute(self, parameters, messages):
        if common_helper.no_processing_directory_selected(parameters, 2):
           return
        
        source_batch_directory_path = workspace_directory.source_batch_directory_path
        csv_files_directory_path = workspace_directory.csv_files_directory_path 
        batch_export_csv.run_tool(source_batch_directory_path, csv_files_directory_path)
        return
    
