import arcpy
import os
import common_helper
import workspace_directory

def add_pyramid_to_geotif_files():
    geofiles = get_filepaths(".tif")
    for geofile in geofiles:
        pyramid(geofile)


def get_filepaths(ext):
    directory = workspace_directory.projected_batch_directory_path
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
        common_helper.output(f"{filepath} - {ex}", 1)

def run_tool():
    add_pyramid_to_geotif_files()
       
