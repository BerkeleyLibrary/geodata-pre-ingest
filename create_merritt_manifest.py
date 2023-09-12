import os
import logging
from pathlib import Path
import csv
import hashlib


################################################################################################
#                             1. functions                                                     #
################################################################################################


def create_merritt_menifest_file(
    main_csv_filepath,
    resp_csv_filepath,
    ingestion_files_directory_path,
    result_directory_path,
):
    name = Path(ingestion_files_directory_path).stem
    menifest_filename = os.path.join(result_directory_path, f"{name}_merritt.txt")
    content = menifest_content(
        main_csv_filepath, resp_csv_filepath, ingestion_files_directory_path
    )

    header = (
        "fileUrl | hashAlgorithm | hashValue | fileSize | fileName | primaryIdentifier | creator | title | date"
        + os.linesep
    )
    with open(menifest_filename, "w") as f:
        f.write(header)
        f.write(content)


def menifest_content(
    main_csv_filepath, resp_csv_filepath, ingestion_files_directory_path
):
    resp_rows = csv_rows(resp_csv_filepath)
    content = ""
    with open(main_csv_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            arkid = row["arkid"]
            creater = get_names(arkid, resp_rows)
            item = menifest_item(row, creater, ingestion_files_directory_path)
            content += item
    return content


def menifest_item(row, creater, ingestion_files_directory_path):
    arkid = row["arkid"]
    data_zip_filename = os.path.join(ingestion_files_directory_path, arkid, "data.zip")
    if not Path(data_zip_filename).is_file():
        text = f"{data_zip_filename} does not exist."
        print(text)
        log_raise_error(text)

    value = hash_value(data_zip_filename)
    size = file_size(data_zip_filename)

    return (
        f"{url(row)}|MD5|{value}|{size}|Data.zip|{primary_identifer(arkid)}|{creater}|{title(row)}|{date(row)}"
        + os.linesep
    )


def url(row):
    arkid = row["arkid"]
    access_right = row["dct_accessRights_s"]
    download_host = (
        "https://spatial.lib.berkeley.edu/public"
        if access_right.lower() == "public"
        else "https://spatial.lib.berkeley.edu/UCB"
    )
    return f"{download_host}/berkeley-{arkid}/data.zip"


def hash_value(data_zip_filename):
    with open(data_zip_filename, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest()
    return md5


def file_size(data_zip_filename):
    size = os.path.getsize(data_zip_filename)
    return str(size)


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
    val = row[name]
    value = val if val else row[f"{name}_o"]
    if name.endswith("m"):
        value = value.replace("$", ";")
    return rm_pipe(value)


def title(row):
    val = col_value(row, "dct_title_s")
    arkid = row["arkid"]
    return f"{val} {primary_identifer(arkid)}"


def date(row):
    return col_value(row, "gbl_mdModified_dt")[:10]


def rm_pipe(str):
    return str.replace("|", "_")


def log_raise_error(text):
    logging.info(text)
    raise ValueError(text)


# having an encoding problem when using csv.DictReader to get a dictionary
# Get lines from CSV can avoid this problem
def csv_rows(csv_filepath):
    lines = (line for line in open(csv_filepath, "r", encoding="utf-8"))
    rows = (line.strip().split(",") for line in lines)
    header = next(rows)
    return [dict(zip(header, row)) for row in rows]


################################################################################################
#                                 2. setup                                                    #
################################################################################################
# 1. setup log file path
logfile = r"D:\Log\shpfile_projection.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 1. Please provide final ingestion files' directory path here
ingestion_files_directory_path = (
    r"D:\pre_test\create_merritt\input\sample_raster_ingestion_files"
)

# 2. Please provide csv file path which have been assigned with arkids
main_csv_filepath = r"D:\pre_test\create_merritt\input\main_sample_raster_arkids.csv"
resp_csv_filepath = r"D:\pre_test\create_merritt\input\resp_sample_raster_arkids.csv"

# 3. please provide output directory to save merritt menifest file
#   attention: Please do not use the original batch directory path or projected directory path
result_directory_path = r"D:\pre_test\create_merritt\result"


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


output(f"*** starting 'creating merritt menifest file'")

if verify_setup(
    [main_csv_filepath, resp_csv_filepath],
    [ingestion_files_directory_path, result_directory_path],
):
    create_merritt_menifest_file(
        main_csv_filepath,
        resp_csv_filepath,
        ingestion_files_directory_path,
        result_directory_path,
    )
    output(f"*** completed: 'creating merritt menifest file'")
