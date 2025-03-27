
import arcpy
import common_helper
import workspace_directory
import check_csv_files
import constants


class CheckCsvFilesTool(object):
    def __init__(self):
        self.label = "4 - Run verification on the main and responsible CSV files that have assigned arkids"

    def getParameterInfo(self):
        main_csv_path_param = arcpy.Parameter(
            displayName="Main csv file",
            name="From main csv file",
            datatype="GPString",
            direction="Output"
        )    
        responsible_csv_path_param = arcpy.Parameter(
            displayName="Responsible csv file",
            name="From responsible csv file",
            datatype="GPString",
            direction="Output"
        )    
        csv_path_param = arcpy.Parameter(
            displayName="Check CSV files located at",
            name="To Directory",
            datatype="GPString",
            direction="Output"

        )
        return [ main_csv_path_param, responsible_csv_path_param, csv_path_param]

    def updateParameters(self, parameters):
        val0 = constants.no_prcess_path_selected
        val1 = val0
        val2 = val0
        if (workspace_directory.source_batch_directory_path is not None):
            csv_files_arkid_directory_path = workspace_directory.csv_files_arkid_directory_path
            val0 = fr"{csv_files_arkid_directory_path}\main_arkid.csv"
            val1 = fr"{csv_files_arkid_directory_path}\resp_arkid.csv"     
        parameters[0].value = val0
        parameters[1].value = val1
        parameters[2].value = csv_files_arkid_directory_path
        return

    def execute(self, parameters, messages):
        common_helper.call_run_tool('check_csv_files')
        return
    
    
