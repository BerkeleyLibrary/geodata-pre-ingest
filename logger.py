import logging
import arcpy

logfile = r"C:\process_data\log\process.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s - %(funcName)s - %(levelname)s",
)

def output(msg):
    logging.info(msg)
    arcpy.AddMessage(msg)
    print(msg)