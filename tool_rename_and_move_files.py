import arcpy
import os
import rename_and_move_files

class RenameAndMoveFilesTool(object):
    def __init__(self):
        self.label = "0 .1 - Move files with lower case extensions"

    def getParameterInfo(self):
        from_dir_path_param = arcpy.Parameter(
            displayName="From directory",
            name="from",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        to_dir_path_param = arcpy.Parameter(
            displayName="To directory",
            name="to",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        
        return [ from_dir_path_param,  to_dir_path_param]

    def execute(self, parameters, messages):

        from_directory_path =  parameters[0].valueAsText
        to_directory_path = parameters[1].valueAsText

        arcpy.AddMessage(f"✅ *** Starting to move batch files from {from_directory_path}")
        rename_and_move_files.run_tool(from_directory_path, to_directory_path)
        arcpy.AddMessage(f"✅ *** Completed moving batch files from {from_directory_path} to {to_directory_path}")
        return