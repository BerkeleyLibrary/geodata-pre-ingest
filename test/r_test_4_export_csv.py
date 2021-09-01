#!/usr/bin/python
import os
import sys
import shutil


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import arcgis_iso_export_csv,arcgis_iso_collection,geo_helper,par
dirname = os.path.dirname(__file__).replace("test","test_data")

# 1) input a directory with tif or shp files
# 2) out put as three csv files
def main():
    try:

        geo_ext = ".tif"
        process_path = os.path.join(dirname,"raster_data","raster")
        workspace_batch_path = geo_helper.GeoHelper.work_path(process_path)

        dest_csv_files = geo_helper.GeoHelper.dest_csv_files(process_path)
        arcGisIso_list = arcgis_iso_collection.ArcGisIsoCollection(workspace_batch_path,geo_ext).all_arcgisiso()

        csv = arcgis_iso_export_csv.ExportCsv(arcGisIso_list,dest_csv_files,geo_ext)
        csv.export_csv_files()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
