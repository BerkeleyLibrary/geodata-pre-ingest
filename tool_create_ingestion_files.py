
import arcpy
import common_helper
import workspace_directory
import create_ingestion_files
import constants

class CreateIngestionFilesTool(object):
    def __init__(self):
        self.label = "7 - Run to create ingestion files for the batch"

    def getParameterInfo(self):
        source_batch_directory_path_param = arcpy.Parameter(
            displayName="The source batch directory",
            name="Source Batch Directory",
            datatype="GPString",
            direction="Output"
        )    
        projected_batch_directory_path = arcpy.Parameter(
            displayName="The projected batch directory",
            name="Projected Batch Directory",
            datatype="GPString",
            direction="Output"

        )
        main_csv_arkid_filepath_param = arcpy.Parameter(
            displayName="The main CSV file",
            name="From main csv file",
            datatype="GPString",
            direction="Output"
        )    
       
        result_directory_path_param = arcpy.Parameter(
            displayName="The result directory",
            name="Result Directory",
            datatype="GPString",
            direction="Output"
        )    
        
        return [ source_batch_directory_path_param, projected_batch_directory_path,
                 main_csv_arkid_filepath_param, result_directory_path_param]

    def updateParameters(self, parameters):
        val0 = val1 = val2 = val3 = constants.no_prcess_path_selected
        if (workspace_directory.source_batch_directory_path is not None):
            val0 = workspace_directory.source_batch_directory_path
            val1 = workspace_directory.projected_batch_directory_path

            csv_files_arkid_directory_path = workspace_directory.csv_files_arkid_directory_path       
            val2 = common_helper.csv_arkid_filepath(csv_files_arkid_directory_path, 'main')
            
            val3 = workspace_directory.results_directory_path
        for i, val in enumerate([val0, val1, val2, val3]):
            parameters[i].value = val
        return

    def execute(self, parameters, messages):
        try:
            create_ingestion_files.run_tool()
        except:
            arcpy.AddError("An error occurred while executing tool_create_ingetion_files.")
            raise

  