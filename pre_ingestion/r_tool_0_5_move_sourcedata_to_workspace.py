#!/usr/bin/python
import os
import sys
import shutil
from geo_helper import GeoHelper
from  geodata_workspace  import GeodataWorkspace
if os.name == "nt":
    import arcpy

def main():
    try:
        geo_ext = '.tif'
        original_source_path = sys.argv[1]
        process_path = sys.argv[2]

        if GeoHelper.has_files(original_source_path) > 0:
            geodata_workspace = GeodataWorkspace(original_source_path,process_path,geo_ext)
            geodata_workspace.excute()
        else:

            GeoHelper.arcgis_message("***Attention***: No source data in directory {0}".format(original_source_path))



    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)

if __name__ == '__main__':
    main()
