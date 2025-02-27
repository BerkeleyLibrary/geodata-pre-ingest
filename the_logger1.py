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
import os

def allow(log_file):
   if os.access(log_file, os.W_OK):
        print (log_file)
        print("✅ Log file is writable.")
   else:
        print (log_file)
        print("❌ Log file is NOT writable. Check permissions.")

def setup_logger(log_dir, log_name="process.log"):    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)  
    
    log_file = os.path.join(log_dir, log_name)
    allow(log_file)
    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("Geoblacklight_Logger")
    logger.setLevel(logging.INFO)
    
    if not logger.hasHandlers():
        print("call adding hander!!!!!!")
        logger.addHandler(handler)

    return logger

def output(log_dir, msg, level="info"):
    logger = setup_logger(log_dir)
    if level.lower() == "error":
        logger.error(msg)
        
    else:
        logger.info(msg)
       
    
    print(msg)  # For debugging in standalone scripts


output(r'D:\zz\log', 'mymy##')
output(r'D:\zz\log', 'mymy12##')