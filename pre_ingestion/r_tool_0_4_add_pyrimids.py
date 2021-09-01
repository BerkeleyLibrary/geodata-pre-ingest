import os
import sys
from geo_helper import GeoHelper
from validate_geodata import ValidateGeodata

def main():
    try:
        original_source_path = sys.argv[1]
        exts = [".tif",".aux",".tfw",".tif.xml",".tif.ovr"]
        geo_ext = '.tif'

        validate_geodata = ValidateGeodata(original_source_path,exts,geo_ext)
        validate_geodata.add_pyrimids()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
