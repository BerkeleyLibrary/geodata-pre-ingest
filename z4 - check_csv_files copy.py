import os
import logging
from pathlib import Path
import csv
from dateutil.parser import parse
from datetime import datetime


################################################################################################
#                             1. functions                                                     #
################################################################################################
def validate_csv_files():
    validate_csv(main_csv_arkid_filepath, func_invalid_cols_from_main_row)
    validate_csv(resp_csv_arkid_filepath, func_invalid_cols_from_resp_row)


def validate_csv(csv_filepath, func):
    row_hash = {}
    num = 1
    with open(csv_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            num += 1
            invalid_cols = func(row)
            if len(invalid_cols):
                arkid = row.get("arkid")
                key = f"line->{num}, arkid->{arkid}:"
                row_hash[key] = invalid_cols
    if row_hash:
        filepath = file_name(csv_filepath, result_directory_path)
        print(f"{csv_filepath} is not valid. Please check details in {filepath}")
        write_file(row_hash, filepath)
    else:
        print(f"{csv_filepath} is valid.")


# resp csv file has no *_O column names
def func_invalid_cols_from_resp_row(row):
    cols = get_empty_cols(row, RESP_REQUIRED_FIELDS)
    cols.extend(invalid_resp_cols(row))
    return cols


def func_invalid_cols_from_main_row(row):
    fieldnames = MAIN_REQUIRED_FIELDS
    if row.get("gbl_resourceClass_sm").lower() == "collections":
        fieldnames = [name for name in fieldnames if name != "geofile"]
        fieldnames.append("doc_zipfile_path")

    cols = get_empty_cols(row, fieldnames)
    cols.extend(invalid_main_value_cols(row))
    cols.extend(invalid_main_date_cols(row))
    cols.extend(invalid_main_range_cols(row))
    return cols


def invalid_main_value_cols(row):
    value_hash = {
        "gbl_resourceClass_sm": LS_gbl_resourceClass_sm,
        "dct_accessRights_s": LS_dct_accessRights_s,
        "dct_format_s": LS_dct_format_s,
    }
    return get_invalid_cols(row, value_hash, get_unexpected_f_v)


def invalid_main_date_cols(row):
    date_hash = {
        "gbl_mdModified_dt": LS_gbl_mdModified_dt,
        "gbl_indexYear_im": LS_gbl_indexYear_im,
        "dct_issued_s": LS_dct_issued_s,
    }
    return get_invalid_cols(row, date_hash, get_invalid_date_f_v)


def invalid_main_range_cols(row):
    range_hash = {"dcat_theme_sm": RG_dcat_theme_sm}
    return get_invalid_cols(row, range_hash, get_invalid_range_f_v)


def get_empty_cols(row, fieldnames):
    empty = []
    for fieldname in fieldnames:
        value = get_value(row, fieldname)
        if not value:
            field_value = f_v(fieldname, ' " " ', "and")
            empty.append(field_value)
    return empty


def get_invalid_cols(row, hash, func):
    invalid = []
    for fieldname, expected_values in hash.items():
        f_v = func(row, fieldname, expected_values)
        if f_v:
            invalid.append(f_v)
    return invalid


def get_value(row, fieldname):
    value = row.get(fieldname)
    if value:
        return value
    o_fieldname = f"{fieldname}_o"
    return row.get(o_fieldname)


def f_v(fieldname, value, word="or"):
    fieldname_o = f"{fieldname}_o"
    new_name = (
        f"{fieldname} {word} {fieldname_o}"
        if fieldname_o in main_csv_headers
        else fieldname
    )
    return [new_name, value]


def get_unexpected_f_v(row, fieldname, expected_values):
    value = get_value(row, fieldname)
    if value:
        vals = value.split("$") if fieldname.endswith("m") else [value]
        for val in vals:
            if not val in expected_values:
                return f_v(fieldname, value)
    return None


def get_invalid_date_f_v(row, fieldname, expected_date_formats):
    value = get_value(row, fieldname)
    if value:
        vals = value.split("$") if fieldname.endswith("m") else [value]
        for val in vals:
            if fieldname == "dct_issued_s":
                val = val.replace('"', "")
            expected = expected_date(val, expected_date_formats)
            if not expected:
                return f_v(fieldname, value)
    return None


def get_invalid_range_f_v(row, fieldname, expected_range):
    value = get_value(row, fieldname)
    if value:
        vals = value.split("$") if fieldname.endswith("m") else [value]
        for val in vals:
            try:
                r = int(val.strip())
                if not r in expected_range:
                    return f_v(fieldname, value)
            except ValueError:
                return [fieldname, f"{fieldname} value '{val}' is not a valid integer"]

    return None


def valid_date(str, format):
    try:
        return bool(datetime.strptime(str, format))
    except ValueError:
        return False


def expected_date(val, formats):
    for format in formats:
        if valid_date(val, format):
            return True
    return False


def csv_headers(csv_filepath):
    with open(csv_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        return csv_reader.fieldnames


def file_name(csvfilepath, output_dir):
    name = Path(csvfilepath).stem
    return os.path.join(output_dir, f"{name}_log.txt")


def write_file(hash, filepath):
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(f"\n Invalid fields:\n")
        for k, ls in hash.items():
            file.write(f"\n {k}:\n")
            for l in ls:
                file.write(f"{l[0]}: {l[1]} \n")


# resp_csv -
# 1. When role is 006 (originator), a row should have either an individual or organization value
# 2. When role is not 006, a row should not allow to have an individual value
# 3. When role is 010 (publisher), it should have an organization value
def invalid_resp_cols(row):
    str = row["role"].strip()
    individual = row["individual"]
    organization = row["organization"]

    if not str:
        return [["role", "Role should not be empty."]]

    try:
        num = int(str)
        if not num in RESP_ROLE:
            return [["role", f"Role value {str} is not between 1 and 11"]]
    except ValueError:
        return [["role", f"Role value '{str}' is not a valid integer"]]

    role = str.zfill(3)
    if role == "006":
        if not organization and not individual:
            return [
                [
                    "individual or organization",
                    "When role = 006, either organization or individual should have a value",
                ]
            ]
    else:
        cols = []
        if individual:
            cols.append(
                [
                    "individual",
                    f"When role != 006, individual should not have a value: {individual}",
                ]
            )

        if role == "010" and not organization:
            cols.append(
                ["organization", "When role = 010, organization should have a value"]
            )

        return cols

    return []


################################################################################################
#                                 2. variables                                                 #
################################################################################################
MAIN_REQUIRED_FIELDS = [
    "arkid",
    "geofile",
    "dct_title_s",
    "gbl_resourceClass_sm",
    "dct_accessRights_s",
    "gbl_mdModified_dt",
    "dct_format_s",
]
LS_gbl_mdModified_dt = ["%Y-%m-%dT%H:%M:%SZ"]
LS_gbl_indexYear_im = ["%Y"]
LS_dct_issued_s = ["%Y", "%Y-%m", "%Y-%m-%d"]
LS_gbl_resourceClass_sm = [
    "Collections",
    "Datasets",
    "Imagery",
    "Maps",
    "Web services",
    "Websites",
    "Other",
]
RG_dcat_theme_sm = range(1, 20)
LS_dct_accessRights_s = ["Public", "Restricted"]
LS_dct_format_s = [
    "ArcGRID",
    "CD-ROM",
    "DEM",
    "DVD-ROM",
    "Feature Class",
    "Geodatabase",
    "GeoJPEG",
    "GeoJSON",
    "GeoPackage",
    "GeoPDF",
    "GeoTIFF",
    "JPEG",
    "JPEG2000",
    "KML",
    "KMZ",
    "LAS",
    "LAZ",
    "Mixed",
    "MrSID",
    "PDF",
    "PNG",
    "Pulsewaves",
    "Raster Dataset",
    "Shapefile",
    "SQLite Database",
    "Tabular Data",
    "TIFF",
]

RESP_REQUIRED_FIELDS = ["arkid", "geofile"]
RESP_ROLE = range(1, 12)
################################################################################################
#                                 3. setup                                                    #
################################################################################################
# 1. setup log file path
logfile = r"C:\process_data\log\process.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 2. Please provide csv files path which have been assigned with arkids
main_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\main_arkid.csv"

resp_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\resp_arkid.csv"


# 3. please provide result directory path:
result_directory_path = r"C:\process_data\csv_files_arkid"


################################################################################################
#                             4. Run
# Example:
# input:
#       main_csv_arkid_filepath = r"D:\results\main_sample_raster_arkids8.csv"
#       resp_csv_arkid_filepath = r"D:\results\main_sample_raster1.csv"
#       result_directory_path = r"D:\results"
# any invalid field values found from above csv files will be written to:
#      D:\results\main_sample_raster_arkids8.txt
#      D:\results\main_sample_raster1.txt
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


main_csv_headers = []


script_name = "4 - check_csv_files.py"
output(f"***starting  {script_name}")

if verify_setup(
    [main_csv_arkid_filepath, resp_csv_arkid_filepath], [result_directory_path]
):
    main_csv_headers = csv_headers(main_csv_arkid_filepath)
    validate_csv_files()
    output(f"***completed {script_name}")
