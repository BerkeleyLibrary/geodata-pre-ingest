#!/usr/bin/python
import os
import sys
import shutil
from arcgis_iso_collection  import ArcGisIsoCollection
from arcgis_iso_export_csv import ExportCsv
from geo_helper import GeoHelper




def main():
    try:
        
        process_path = sys.argv[1]
        geo_ext = ".tif"

        workspace_batch_path = GeoHelper.work_path(process_path)
        arcGisIso_list = ArcGisIsoCollection(workspace_batch_path,geo_ext).all_arcgisiso()

        dest_csv_files = GeoHelper.dest_csv_files(process_path)
        csv = ExportCsv(arcGisIso_list,dest_csv_files,geo_ext)
        csv.export_csv_files()

        if os.name == "nt":
            csv_path = GeoHelper.csv_path(process_path)
            arcpy.RefreshCatalog(csv_path)

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
