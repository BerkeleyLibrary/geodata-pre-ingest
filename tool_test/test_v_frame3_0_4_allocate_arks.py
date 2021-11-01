import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pre_ingestion import assign_arks,geo_helper

dirname = os.path.dirname(__file__).replace("test","test_data")


def main():
    try:
        process_path = os.path.join(dirname,"vector_data","vector_frame")
        ark_txt = os.path.join(process_path,"arks.txt")

        arks = assign_arks.AssignArks(process_path,ark_txt,'.shp')
        arks.excute()

    except Exception, e:
        txt = "Code exception: {0}  ;   {1}".format(__file__,str(e))
        geo_helper.GeoHelper.arcgis_message(txt)



if __name__ == '__main__':
    main()
