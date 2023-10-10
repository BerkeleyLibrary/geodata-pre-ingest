import os
import logging
from pathlib import Path
import csv
import hashlib


################################################################################################
#                             1. functions                                                     #
################################################################################################


def create_merritt_menifest_file():
    # name = Path(ingestion_files_directory_path).stem
    menifest_filename = os.path.join(result_directory_path, f"merritt.txt")
    content = menifest_content()
    header = (
        "fileUrl | hashAlgorithm | hashValue | fileSize | fileName | primaryIdentifier | creator | title | date"
        + os.linesep
    )
    with open(menifest_filename, "w") as f:
        f.write(header)
        f.write(content)


def menifest_content():
    resp_rows = resp_csv_dict_list()
    content = ""
    with open(main_csv_arkid_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            if row.get("gbl_resourceClass_sm").lower() != "collections":
                item = menifest_item(row, resp_rows)
                content += item
    return content


def menifest_item(row, resp_rows):
    arkid = row.get("arkid")
    access_right = row.get("dct_accessRights_s")
    dct_title_s = col_value(row, "dct_title_s")
    md_date = col_value(row, "gbl_mdModified_dt")[:10]
    creater = get_names(arkid, resp_rows)

    data_zip_filename = os.path.join(ingestion_files_directory_path, arkid, "data.zip")

    value = hash_value(data_zip_filename)
    size = file_size(data_zip_filename)

    return (
        f"{url(arkid, access_right)}|MD5|{value}|{size}|Data.zip|{primary_identifer(arkid)}|{creater}|{title(arkid, dct_title_s)}|{md_date}"
        + os.linesep
    )


def url(arkid, access_right):
    access = access_right.lower()
    if access == "public":
        download_host = host_public
    elif access_right == "restricted":
        download_host = host_restricted
    else:
        print("dct_accessRights_s value is neither public nor restricted")
        raise ValueError

    return f"{download_host}/berkeley-{arkid}/data.zip"


def hash_value(data_zip_filename):
    try:
        with open(data_zip_filename, "rb") as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        return md5
    except FileNotFoundError as e:
        txt = f"File not found: {data_zip_filename} {e}"
        print(txt)
        log_raise_error(txt)


def file_size(data_zip_filename):
    try:
        size = os.path.getsize(data_zip_filename)
        return str(size)
    except FileNotFoundError as e:
        txt = f"File not found: {data_zip_filename} {e}"
        print(txt)
        log_raise_error(txt)


def primary_identifer(arkid):
    return f"ark:/28722/{arkid}"


def get_names(arkid, resp_rows):
    names = []
    for resp_row in resp_rows:
        name = resp_row.get("individual") or resp_row.get("organization")
        if (
            arkid == resp_row.get("arkid")
            and resp_row.get("role").strip().zfill(3) == "006"
            and name
        ):
            names.append(name)

    return ",".join(names)


def col_value(row, name):
    val = row.get(name)
    value = val if val else row.get(f"{name}_o")
    if name.endswith("m"):
        value = value.replace("$", ";")
    return rm_pipe(value)


def title(arkid, dct_title_s):
    return f"{dct_title_s} {primary_identifer(arkid)}"


def date(row):
    return col_value(row, "gbl_mdModified_dt")[:10]


def rm_pipe(str):
    return str.replace("|", "_")


def log_raise_error(text):
    logging.info(text)
    raise ValueError(text)


# having an encoding problem when using csv.DictReader to get a dictionary
# Get lines from CSV can avoid this problem
def resp_csv_dict_list():
    lines = (line for line in open(resp_csv_arkid_filepath, "r", encoding="utf-8"))
    rows = (line.strip().split(",") for line in lines)
    header = next(rows)
    return [dict(zip(header, row)) for row in rows]


################################################################################################
#                                 2. setup                                                    #
################################################################################################

host_public = "https://spatial.lib.berkeley.edu/public"
host_restricted = "https://spatial.lib.berkeley.edu/UCB"

# 1. setup log file path
logfile = r"C:\process_data\log\process.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 1. Please provide final ingestion files' directory path here
ingestion_files_directory_path = r"C:\process_data\results\ingestion_files"


# 2. Please provide csv file path which have been assigned with arkids
main_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\main_arkid.csv"
resp_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\resp_arkid.csv"

# 3. please provide output directory to save merritt menifest file
#   attention: Please do not use the original batch directory path or projected directory path
result_directory_path = r"C:\process_data\results"


################################################################################################
#                             3. Create the merritt menifest file
################################################################################################
def output(msg):
    logging.info(msg)
    print(msg)


def verify_setup(file_paths, directory_paths):
    verified = True
    for file_path in file_paths:
        if not Path(file_path).is_file():
            print(f"{file_path} does not exit.")
            verified = False

    for directory_path in directory_paths:
        if not Path(directory_path).is_dir():
            print(f"{directory_path} does not exit.")
            verified = False
    return verified


script_name = "9 - create_merritt_manifest.py"
output(f"***starting  {script_name}")

if verify_setup(
    [main_csv_arkid_filepath, resp_csv_arkid_filepath],
    [ingestion_files_directory_path, result_directory_path],
):
    create_merritt_menifest_file()
    output(f"***completed {script_name}")
