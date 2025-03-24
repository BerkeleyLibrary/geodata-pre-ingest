
import arcpy
import common_helper
import workspace_directory
import batch_create_iso19139
import constants

class BatchCreateIso19139Tool(object):
    def __init__(self):
        self.label = "5 - Run to create ISO19139 xml files for the batch"

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
            displayName="Main csv file",
            name="From main csv file",
            datatype="GPString",
            direction="Output"
        )    
        resp_csv_arkid_filepath_param = arcpy.Parameter(
            displayName="Responsible csv file",
            name="From responsible csv file",
            datatype="GPString",
            direction="Output"
        )    
        
        return [ source_batch_directory_path_param, projected_batch_directory_path, main_csv_arkid_filepath_param, resp_csv_arkid_filepath_param]

    def updateParameters(self, parameters):
        val0 = val1 = val2 = val3 = constants.no_prcess_path_selected
        if (workspace_directory.source_batch_directory_path is not None):
            val0 = workspace_directory.source_batch_directory_path
            val1 = workspace_directory.projected_batch_directory_path
            csv_files_arkid_directory_path = workspace_directory.csv_files_arkid_directory_path  
            val2 = fr"{csv_files_arkid_directory_path }\main_arkid.csv"
            val3 = fr"{csv_files_arkid_directory_path }\resp_arkid.csv"       

        for i, val in enumerate([val0, val1, val2, val3]):
            parameters[i].value = val
        return

    def execute(self, parameters, messages):
        try:
            common_helper.verify_selected_source_batch_directory(parameters, 4)
            batch_create_iso19139.run_tool()

        except:
            arcpy.AddError("An error occurred while executing tool_batch_create_iso19139.")
            raise
