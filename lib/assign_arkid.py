import requests
import csv
import os
from pathlib import Path
import json
import common_helper
import workspace_directory


################################################################################################
#                             1. functions                                                      #
################################################################################################


def mint_ark():
    config = ez_config()
    url = config["url"]
    namespace = config["namespace"]
    auth = (config["username"], config["password"])

    try:
        response = requests.post(f"{url}{namespace}", auth=auth)
        if response.status_code == 201:
            # eg. "ark:/99999/fk4m34f494"
            return response.text.split("/")[-1]
        else:
            log_raise_error(
                f"Mint arkid request failed. Status code: {response.status_code}"
            )
    except requests.RequestException as e:
        log_raise_error(f"Failed to make a mint arkid request: {e}")


def rows_with_arkid(csv_path, hash=None):
    rows = []
    try:
        with open(csv_path, "r", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            need_mint_ark = hash is None
            for row in csv_reader:
                row_arkid = row.get("arkid")
                if not row_arkid:
                    add_mint_arkid(row) if need_mint_ark else add_hash_arkid(row, hash)
                rows.append(row)

        return rows
    except FileNotFoundError as e:
        log_raise_error(f"File not found: {csv_path} {e}")
    except csv.Error as e:
        log_raise_error(f"CSV Error while reading file: {csv_path} {e}")
    except Exception as e:
        log_raise_error(f"Unexpected error while reading file: {csv_path} {e}")


def add_mint_arkid(row):
    arkid = mint_ark()
    row["arkid"] = arkid


def add_hash_arkid(row, hash):
    geofile = row.get("geofile")
    arkid = hash.get(geofile)
    if arkid:
        row["arkid"] = arkid
    else:
        msg = f"No arkid in main_csv file for geofile {geofile}"
        log_raise_error(msg)

def log_raise_error(msg):
    common_helper.output(msg, 1)
    # logging.exception(msg)
    raise ValueError(msg)


def is_assigned(file):
    with open(file, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            arkid = row["arkid"]
            if not arkid:
                return False
    return True


def assign_main_csv(main_csv_filepath, new_main_csv_filepath):
    rows = rows_with_arkid(main_csv_filepath)
    write_csv(main_csv_filepath, rows)
    write_csv(new_main_csv_filepath, rows)
   
def assign_resp_csv(resp_csv_filepath, new_main_csv_filepath, new_resp_csv_filepath):
    hash = arkid_hash(new_main_csv_filepath)
    if hash:
        rows = rows_with_arkid(resp_csv_filepath, hash)
        write_csv(resp_csv_filepath, rows)
        write_csv(new_resp_csv_filepath, rows)
    else:
        log_raise_error(f"no arkid or geofile ?, please check {new_main_csv_filepath}")


def arkid_hash(csv_filepath):
    hash = {}
    with open(csv_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            hash[row.get("geofile")] = row.get("arkid")
    return hash


def write_csv(filename_path, rows):
    if rows:
        with open(filename_path, "w", newline="", encoding="utf-8") as file:
            headers = rows[0].keys()
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
    else:
        log_raise_error(f"no rows to add to {filename_path}")


def ez_config():
    with open(config_file, "r") as f:
        return json.load(f)


def new_filepath(csv_files_arkid_directory_path, filepath):
    filename = Path(filepath).stem
    return os.path.join(csv_files_arkid_directory_path, f"{filename}_arkid.csv")


################################################################################################
#                                 2. set up                                                    #
################################################################################################

# # 1. Please provide your local log file path
# logfile = r"C:\process_data\log\process.log"
# logging.basicConfig(
#     filename=logfile,
#     level=logging.INFO,
#     format="%(message)s - %(asctime)s - %(funcName)s - %(levelname)s",
# )

# 2. please provide EZID config file path
config_file = r"C:\pre-ingestion-config/config.json"

# # 3. please provide main_csv file path:
# main_csv_filepath = r"C:\process_data\csv_files\main.csv"

# # 4. please provide resp_csv file path:
# resp_csv_filepath = r"C:\process_data\csv_files\resp.csv"

# # 5. Place to save the new main csv file and resp csv file with arkid assigned
# csv_files_arkid_directory_path = r"C:\process_data\csv_files_arkid"


################################################################################################
#                                3. instructions
#  a. mian_csv file:
#                a new arkid will be minted and added to the 'arkid' column for each row,
#                unless a row has an existing arkid.
#  b. resp_csv file:
#               - 'arkid' column will be updated with 'arkid' value from main_csv file
#                based on the column 'geofile' value(geofile name path) from both files .
#               -  One row in main_csv file may be related to multiple rows in resp_csv file
#  c: after running this script two output files will be generated with arkids assigned
#  d: original csv files will have arkid assigned
#  C: new files will be named as "*_arkids.csv"
#  example:
#         input two files:
#                       main_csv_filepath = r"C:\process_data\csv_files\main.csv"
#                       resp_csv_filepath = r"C:\process_data\csv_files\resp.csv"
#         output path:
#                       csv_files_arkid_directory_path = r"C:\process_data\csv_files_arkid"
#         two new file paths (*_arkids.csv) are:
#                                        "C:\process_data\csv_files_arkid\main_arkid.csv"
#                                        "C:\process_data\csv_files_arkid\resp_arkid.csv"
################################################################################################

def run_tool():
    csv_files_directory_path = workspace_directory.csv_files_directory_path
    main_csv_filepath = fr"{csv_files_directory_path}\main.csv"
    resp_csv_filepath = fr"{csv_files_directory_path}\resp.csv"     
    csv_files_arkid_directory_path = workspace_directory.csv_files_arkid_directory_path   
    common_helper.output(fr"*** Starting to assign arkids to {csv_files_arkid_directory_path}")
    if not common_helper.verify_setup([main_csv_filepath, resp_csv_filepath], [csv_files_arkid_directory_path]):
        return 
    
    new_main_csv_filepath = new_filepath(csv_files_arkid_directory_path, main_csv_filepath)
    new_resp_csv_filepath = new_filepath(csv_files_arkid_directory_path, resp_csv_filepath)
    
    # step 1. Add arkids to rows in main.csv file (if missing)
    assign_main_csv(main_csv_filepath, new_main_csv_filepath)
   
    # step 2. Assign ARKIDs to resp CSV if main CSV assignment was successful
    if is_assigned(new_main_csv_filepath):
        assign_resp_csv(resp_csv_filepath, new_main_csv_filepath, new_resp_csv_filepath)
    else:
        msg = f"failed in updating arkids to {new_resp_csv_filepath}, since {new_main_csv_filepath} missing arkids"
        common_helper.output(msg, 1)
        return

    # Step 3: Warn if new_resp_csv_filepath still has missing ARKIDs
    if not is_assigned(new_resp_csv_filepath):
        msg = f" {resp_csv_filepath} has missing arkids, please check log file for details"
        common_helper.output(msg, 1)
        return

    # If all steps completed successfully
    common_helper.output("*** ARKID assignment completed successfully.", 0)
