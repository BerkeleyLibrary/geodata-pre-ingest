import arcpy
import os
import common_helper


################################################################################################
#                             1. functions                                                        #
################################################################################################


def add_pyramid_to_geotif_files(projected_batch_directory_path):
    geofiles = get_filepaths(projected_batch_directory_path, ".tif")
    for geofile in geofiles:
        pyramid(geofile)


def get_filepaths(directory, ext):
    paths = []
    for file in os.listdir(directory):
        if file.endswith(ext):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                paths.append(file_path)
    return paths


def pyramid(filepath):
    pylevel = "7"
    skipfirst = "NONE"
    resample = "NEAREST"
    compress = "Default"
    quality = "70"
    skipexist = "SKIP_EXISTING"
    try:
        arcpy.management.BuildPyramids(
            filepath, pylevel, skipfirst, resample, compress, quality, skipexist
        )
    except Exception as ex:
        # logging.info(f"{filepath} - {ex}")
        common_helper.output(f"{filepath} - {ex}", 1)



################################################################################################
#                                2. Run options                                                #
################################################################################################
def run_tool(projected_batch_directory_path):
    if common_helper.verify_setup(
            [],
            [projected_batch_directory_path],
        ):
            common_helper.output(f"Starting to add pyramids to: {projected_batch_directory_path}")
            add_pyramid_to_geotif_files(projected_batch_directory_path)
            common_helper.output(f"Completed to adding pyramids to: {projected_batch_directory_path}")

