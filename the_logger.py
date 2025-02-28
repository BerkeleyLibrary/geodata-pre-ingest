# import logging
# import arcpy

# logfile = r"C:\process_data\log\process.log"
# logging.basicConfig(
#     filename=logfile,
#     level=logging.INFO,
#     format="%(message)s - %(asctime)s - %(funcName)s - %(levelname)s",
# )

# def output(msg):
#     logging.info(msg)
#     arcpy.AddMessage(msg)
#     print(msg)


import logging
import arcpy
import os
from logging.handlers import RotatingFileHandler

def allow(log_file):
   if os.access(log_file, os.W_OK):
        
        print (log_file)
        print("✅ Log file is writable.")
        arcpy.AddMessage('writable')
   else:
        arcpy.AddMessage('not writable')
        print (log_file)
        print("❌ Log file is NOT writable. Check permissions.")

def setup_logger(log_dir, log_name="process.log"):        
    log_file = os.path.join(log_dir, log_name)
    logger = logging.getLogger("MyLogger")
    logger.setLevel(logging.INFO)

    # Use rotating file handler to avoid locking issues
    handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
  
    logger.addHandler(handler)

    # logger.info("Logging with rotating file handler.")

    return logger



def setup_logger1(log_dir, log_name="process.log"):    
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir)  
    
    log_file = os.path.join(log_dir, log_name)
    # allow(log_file)
    handler = logging.FileHandler(log_file, encoding="utf-8", mode="w")
    # handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=3, encoding="utf-8")
    # formatter = logging.Formatter(
    #     "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
    # )
    # handler.setFormatter(formatter)
    # handler.flush()

    logger = logging.getLogger("Geoblacklight_Logger")
    # logger.setLevel(logging.INFO)
    
    if not logger.hasHandlers():
        arcpy.AddMessage("call adding hander!!!!!!")
        logger.addHandler(handler)
        

    return logger

def output(log_dir, msg, level="info"):
    log_file = os.path.join(log_dir, "process.log")
    
    logger = setup_logger(log_dir)
    if level.lower() == "error":
        logger.error(msg)
        arcpy.AddError(msg)
    else:
        logger.info(msg)
        arcpy.AddMessage(msg)
        # arcpy.AddMessage("!!!! should save to local file")
        # allow(log_file)
    
    # print(msg)  # For debugging in standalone scripts


# output(r'D:\zz\log', 'mymy')