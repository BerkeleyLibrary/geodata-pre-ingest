#!/usr/bin/python
import os
import sys
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import csv_tranform,csv_iso_collection,geo_helper,par,validate_csv
dirname = os.path.dirname(__file__).replace("test","test_data")


def main():
    try:
        process_path = os.path.join(dirname,"raster_data","raster_export")
        valid_updated_csv = validate_csv.ValidateCSV(process_path)

        if valid_updated_csv.updated_csv_files_existed():
            if valid_updated_csv.updated_csv_files_valid():
                updated_csv_files = geo_helper.GeoHelper.dest_csv_files_updated(process_path)
                csv_collection = csv_iso_collection.CsvIsoCollection(updated_csv_files).csv_collection()
                csvtransform = csv_tranform.CsvTransform(csv_collection,process_path)
                csvtransform.transform_geoblacklight()
                if os.name == "nt":
                    arcpy.RefreshCatalog(geoblacklight_dir)

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)

if __name__ == '__main__':
    main()
