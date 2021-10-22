#!/usr/bin/python
import os
import sys
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import geo_validation,geo_helper
dirname = os.path.dirname(__file__)
data_dirname = os.path.dirname(__file__).replace("test","test_data")


def main():
    try:
        geoblacklight_file = os.path.join(data_dirname,"raster_data","raster_export","Results","precessed_result","Geoblacklight Json Files","b8gq99","geoblacklight.json")
        json_schema = os.path.join(dirname,"validation","geoblacklight-schema-aardvark.json")
        validate = GeoValidation(geoblacklight_file,json_schema).isValidGeoJson()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)

if __name__ == '__main__':
    main()
