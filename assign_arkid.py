import requests
import logging
import csv
import os
from pathlib import Path


################################################################################################
#                             1. functions                                                      #
################################################################################################
def mint_ark():
    url = ""
    username = ""
    password = ""

    auth = (username, password)
    response = requests.post(url, auth=auth)

    if response.status_code == 201:
        return response.text.split("/")[-1]
    else:
        log_raise_error(
            f"Mint arkid request failed. Status code: {response.status_code}"
        )


# if column arkid has value, no arkid added
# if has existing arkid hash, adding arkid from the hash
def add_arkids_rows(csv_path, hash=None):
    rows = []
    need_new_arkid = False if hash else True
    try:
        with open(csv_path, "r", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                if not row["arkid"]:
                    id = mint_ark() if need_new_arkid else hash[row["geofile"]]
                    if id:
                        row["arkid"] = id
                    elif not need_new_arkid:
                        logging.info(
                            f"no arkid in main_csv file for geofile {row['geofile']}"
                        )
                rows.append(row)
        return rows
    except FileNotFoundError:
        log_raise_error(f"File not found: {csv_path}")
    except csv.Error as e:
        log_raise_error(f"CSV Error while reading file: {csv_path} {e.args}")
    except Exception as e:
        log_raise_error(f"Unexpected error while reading file: {csv_path} {e.args}")


def log_raise_error(msg):
    logging.exception(msg)
    raise ValueError(msg)


def has_arkid_added(file):
    with open(file, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            arkid = row["arkid"]
            if not arkid:
                return False
    return True


def update_main_csv(main_csv_path):
    rows = add_arkids_rows(main_csv_path)
    new_filename_path = add_arkid_to_name(main_csv_path)
    write_csv(new_filename_path, rows)


def update_resp_csv(main_csv_path, resp_csv_path):
    hash = arkid_hash(main_csv_path)
    if hash:
        rows = add_arkids_rows(resp_csv_path, hash)
        new_filename_path = add_arkid_to_name(resp_csv_path)
        write_csv(new_filename_path, rows)
    else:
        log_raise_error(f"no arkid or geofile ?, please check {main_csv_path}")


def arkid_hash(main_csv):
    hash = {}
    with open(main_csv, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            hash[row["geofile"]] = row["arkid"]
    return hash


def add_arkid_to_name(filename_path):
    base = os.path.splitext(filename_path)[0]
    return f"{base}_arkids.csv"


def write_csv(filename_path, rows):
    if rows:
        with open(filename_path, "w", newline="", encoding="utf-8") as file:
            headers = rows[0].keys()
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
    else:
        log_raise_error(f"no rows to add to {filename_path}")


################################################################################################
#                                 2. set up                                                    #
################################################################################################

# 1. Please provide your local log file path
logfile = r"D:\Log\shpfile_projection.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s - %(funcName)s - %(levelname)s",
)

# 2. please provide EZID url, username and password at script in section 1

# 3. please provide main_csv file path:
main_csv_path = r"D:\results\main_test_vector_workspace_2023-08.csv"

# 4. please provide resp_csv file path:
resp_csv_path = r"D:\results\resp_test_vector_workspace_2023-08.csv"


################################################################################################
#                                3. instructions
#  a. mian_csv file:
#                a new arkid will be minted and added to the 'arkid' column for each row,
#                unless the 'arkid' column has an existing value.
#  b. resp_csv file:
#               - 'arkid' column will be updated by using 'arkid' column from main_csv file
#                based on the column 'geofile' value(geofile name path) from both files .
#               -  One row in main_csv file may be related to multiple rows in resp_csv file
#  c: after running this script two output files will be generated with arkids assigned
#  d: new files will be named as "*_arkids.csv"
#  example:
#         input two files:
#                       main_csv_path = r"D:\results\main_test_vector_workspace_2023-08.csv"
#                       resp_csv_path = r"D:\results\resp_test_vector_workspace_2023-08.csv"
#         output two files (*_arkids.csv) will look like below:
#                                        "D:\results\main_test_vector_workspace_2023-08_arkids.csv"
#                                        "D:\results\resp_test_vector_workspace_2023-08_arkids.csv"
################################################################################################
def output(msg):
    logging.info(msg)
    print(msg)


def verify_setup(*args):
    verified = True
    for arg in args:
        if not Path(arg).is_file():
            print(f"{arg} does not exit.")
            verified = False

    return verified


output(f"***starting 'assign_arkid'")

if verify_setup(main_csv_path, resp_csv_path):
    # 1. add arkids to main_csv file:
    # it will only add arkids to rows which have no existing arkids
    updated_main_csv_path = add_arkid_to_name(main_csv_path)
    updated_resp_csv_path = add_arkid_to_name(resp_csv_path)
    update_main_csv(main_csv_path)

    # 2. add arkids to resp_csv file based on main_csv file
    if has_arkid_added(updated_main_csv_path):
        update_resp_csv(updated_main_csv_path, resp_csv_path)
    else:
        log_raise_error(
            f"failed in updating arkids to {resp_csv_path}, since {updated_main_csv_path} missing arkids"
        )

    # 3. check arkid exists in resp_csv file
    if not has_arkid_added(updated_resp_csv_path):
        log_raise_error(
            f" {resp_csv_path} has missing arkids, please check log file for details"
        )

    output(f"***completed 'assign_arkid'")
