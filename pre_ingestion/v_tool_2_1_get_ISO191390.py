#!/usr/bin/python
import os
import sys
from csv_iso_collection import  CsvIsoCollection
from csv_tranform import CsvTransform
from validate_csv import ValidateCSV

from geo_helper import GeoHelper


# 1. Source: updated csv files - modified metadata
# 2. output to two places: a) ISO19139 directory,  b) source data directory

def main():
    try:
        process_path = sys.argv[1]
        valid_updated_csv = ValidateCSV(process_path)

        if valid_updated_csv.updated_csv_files_existed():
            if valid_updated_csv.updated_csv_files_valid():

                updated_csv_files = GeoHelper.dest_csv_files_updated(process_path)
                csv_collection = CsvIsoCollection(updated_csv_files).csv_collection()
                csvtransform = CsvTransform(csv_collection,process_path)
                csvtransform.transform_iso19139()
                
                output_iso19139_dir =  GeoHelper.iso19139_path(process_path)
                arcpy.RefreshCatalog(output_iso19139_dir)



    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)

if __name__ == '__main__':
    main()
