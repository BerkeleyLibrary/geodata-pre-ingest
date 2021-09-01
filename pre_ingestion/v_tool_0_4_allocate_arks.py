import os
import sys
from geo_helper import GeoHelper
from assign_arks import AssignArks
if os.name == "nt":
    import arcpy

def main():
    try:
        process_path = sys.argv[1]
        ark_txt = os.path.join(process_path,"arks.txt")
        geo_ext = ".shp"

        assign_arks = AssignArks(process_path,ark_txt,geo_ext)
        assign_arks.excute()
        if os.name == "nt":
            arcpy.RefreshCatalog(process_path)

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        GeoHelper.arcgis_message(txt)


if __name__ == '__main__':
    main()
