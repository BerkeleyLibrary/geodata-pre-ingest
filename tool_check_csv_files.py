
import arcpy
import common_helper
import workspace_directory
import constants


class CheckCsvFilesTool(object):
    def __init__(self):
        self.label = "4 - Run to verify the main and responsible CSV files which have been assigned arkids"

    def getParameterInfo(self):
        csv_path_param = arcpy.Parameter(
            displayName="Check CSV files located at",
            name="To Directory",
            datatype="GPString",
            direction="Output"

        )
        return [csv_path_param]

    def updateParameters(self, parameters):
        val0 =  constants.no_prcess_path_selected
        if (workspace_directory.source_batch_directory_path is not None):
          val0 = workspace_directory.csv_files_arkid_directory_path
       
        parameters[0].value = val0
        return


    def execute(self, parameters, messages):
        common_helper.call_run_tool('check_csv_files')
        return
    
    
