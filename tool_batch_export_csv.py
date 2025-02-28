
import arcpy
import common_helper
import workspace_directory
import batch_export_csv
import instances
import the_logger


class BatchExportCsvTool(object):
    def __init__(self):
        self.label = "2 - Export metadata to a CSV file"
        

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
        source_batch_directory_path = workspace_directory.source_batch_directory_path
        csv_files_directory_path = workspace_directory.csv_files_directory_path 

        if common_helper.stop_execute(parameters, 2):
             # no workspace_directory.logger because of no process directory selected yet
             arcpy.AddError("Error: ❌ no data process path was selected yet, cannot export a CSV file")
             return
            #  raise arcpy.ExecuteError
        
        # path = workspace_directory.log_directory_path
        # logger = workspace_directory.logger
        # common_helper.output(logger,path)
        common_helper.output(fr"Starting to export csv file from - {source_batch_directory_path}")
        if common_helper.verify_setup([], [source_batch_directory_path, csv_files_directory_path]):
            batch_export_csv.run_tool(source_batch_directory_path, csv_files_directory_path)
            common_helper.output(fr"Completed to export csv file from - {source_batch_directory_path}")
        return

    
