#!/usr/bin/python
import os
import sys
from csv_iso_collection import  CsvIsoCollection
from csv_tranform import CsvTransform
from geo_helper import GeoHelper
from validate_csv import ValidateCSV

# 1. From: 1) updated csv files; 2)iso19139 xml files; 3)fixed metadata from par
# 2. output: result geoblacklight directory

def main():
    try:
        process_path = sys.argv[1]
        valid_updated_csv = ValidateCSV(process_path)

        if valid_updated_csv.updated_csv_files_existed():
            if valid_updated_csv.updated_csv_files_valid():
                updated_csv_files = GeoHelper.dest_csv_files_updated(process_path)
                csv_collection = CsvIsoCollection(updated_csv_files).csv_collection()
                csvtransform = CsvTransform(csv_collection,process_path)
                csvtransform.transform_geoblacklight()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
