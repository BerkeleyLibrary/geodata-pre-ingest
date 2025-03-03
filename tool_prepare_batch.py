
import arcpy
import logging
import common_helper
import workspace_directory
import prepare_batch
import instances

class PrepareBatchTool(object):
    def __init__(self):
        self.label = "1 .1 - Run to prepare_batch"
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
        val0= instances.no_prcess_path_selected
        val1= val0
        if (workspace_directory.projected_batch_directory_path is not None):
            val0= workspace_directory.source_batch_directory_path
            val1= workspace_directory.projected_batch_directory_path            
        parameters[0].value = val0
        parameters[1].value = val1
        return

    def execute(self, parameters, messages):
        if common_helper.no_processing_directory_selected(parameters, 2):
           return
            
        source_batch_directory_path = workspace_directory.source_batch_directory_path
        projected_batch_directory_path = workspace_directory.projected_batch_directory_path
        prepare_batch.run_tool(source_batch_directory_path, projected_batch_directory_path)
        return

        # # A GeoTIFF projected file
        # geotif_referenced_filepath = (
        #     r"C:\pre-ingestion-config\projected_raster\5048_1_reproject4326.tif"
        # )

        # if common_helper.verify_setup(
        #     [geotif_referenced_filepath],
        #     [source_batch_directory_path, projected_batch_directory_path],
        # ):
        #     common_helper.output("Starting preparing batch")
        #     source_batch = prepare_batch.SourceBatch(source_batch_directory_path, logging)
        #     source_batch.check_files() # todo: move this to other tool
        #     source_batch.prepare(projected_batch_directory_path, geotif_referenced_filepath)
        #     common_helper.output("Completed preparing batch")
       

    
