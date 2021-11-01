#!/usr/bin/python
import os
import sys
import shutil

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import geodata_workspace,geo_helper
dirname = os.path.dirname(__file__).replace("test","test_data")

def main():
    try:
        geo_ext = '.tif'
        original_source_path =  os.path.join(dirname,"raster_data","raster_original_source")
        process_path = os.path.join(dirname,"raster_data","raster_frame")
        geoworkspace = geodata_workspace.GeodataWorkspace(original_source_path,process_path,geo_ext)
        geoworkspace.excute()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)



if __name__ == '__main__':
    main()
