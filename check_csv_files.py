import os
import logging
from pathlib import Path
import csv
from dateutil.parser import parse
from datetime import datetime


################################################################################################
#                             1. functions                                                     #
################################################################################################
def validate_csv_files(main_csv_filepath, resp_csv_filepath, output_dir):
    validate_csv(main_csv_filepath, output_dir, validate_main_row)
    validate_csv(resp_csv_filepath, output_dir, validate_resp_row)


def validate_csv(csv_filepath, output_dir, func):
    row_hash = {}
    num = 1
    with open(csv_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            num += 1
            invalid_cols = func(row)
            if len(invalid_cols):
                arkid = row.get("arkid")
                key = f"line{num}, arkid - {arkid}"
                row_hash[key] = invalid_cols
    if row_hash:
        filepath = file_name(csv_filepath, output_dir)
        print(f"{csv_filepath} is not valid. Please check details in {filepath}")
        write_file(row_hash, filepath)
    else:
        print(f"{csv_filepath} is valid.")


# resp csv file does not have *_O field
def validate_resp_row(row):
    return get_empty_cols(row, ["arkid", "geofile"])


def validate_main_row(row):
    cols = get_empty_cols(row, required_fields)
    cols.extend(invalid_value_cols(row))
    cols.extend(invalid_date_cols(row))
    cols.extend(invalid_range_cols(row))
    return cols


def invalid_value_cols(row):
    value_hash = {
        "gbl_resourceClass_sm": ls_gbl_resourceClass_sm,
        "dct_accessRights_s": ls_dct_accessRights_s,
        "dct_format_s": ls_dct_format_s,
    }
    return get_invalid_cols(row, value_hash, get_unexpected_f_v)


def invalid_date_cols(row):
    date_hash = {
        "gbl_mdModified_dt": ls_gbl_mdModified_dt,
        "gbl_indexYear_im": ls_gbl_indexYear_im,
        "dct_issued_s": ls_dct_issued_s,
    }
    return get_invalid_cols(row, date_hash, get_invalid_date_f_v)


def invalid_range_cols(row):
    range_hash = {"dcat_theme_sm": rg_dcat_theme_sm}
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
            expected = expected_date(val, expected_date_formats)
            if not expected:
                return f_v(fieldname, value)
    return None


def get_invalid_range_f_v(row, fieldname, expected_range):
    value = get_value(row, fieldname)
    if value:
        vals = value.split("$") if fieldname.endswith("m") else [value]
        for val in vals:
            r = int(val.strip())
            if not r in expected_range:
                return f_v(fieldname, value)
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
    return os.path.join(output_dir, f"{name}.txt")


def write_file(hash, filepath):
    with open(filepath, "w") as file:
        file.write(f"\n Invalid fields:\n")
        for k, ls in hash.items():
            file.write(f"\n {k}:\n")
            for l in ls:
                file.write(f"{l[0]}: {l[1]} \n")


################################################################################################
#                                 2. variables                                                 #
################################################################################################
required_fields = [
    "arkid",
    "geofile",
    "dct_title_s",
    "ls_gbl_resourceClass_sm",
    "dct_accessRights_s",
    "gbl_mdModified_dt",
    "ls_dct_format_s",
]
ls_gbl_mdModified_dt = ["%Y%m%d"]
ls_gbl_indexYear_im = ["%Y"]
ls_dct_issued_s = ["%Y", "%Y-%m", "%Y-%m-%d"]
ls_gbl_indexYear_im = "%Y"
ls_gbl_resourceClass_sm = [
    "Collections",
    "Datasets",
    "Imagery",
    "Maps",
    "Web services",
    "Websites",
    "Other",
]
rg_dcat_theme_sm = range(1, 20)
ls_dct_accessRights_s = ["Public", "Restricted"]
ls_dct_format_s = [
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
################################################################################################
#                                 3. setup                                                    #
################################################################################################
# 1. setup log file path
logfile = r"D:\Log\shpfile_projection.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 2. Please provide csv files path which have been assigned with arkids
main_csv_filepath = r"D:\pre_test\validate_csv\input\main_sample_raster_arkids8.csv"
resp_csv_filepath = r"D:\pre_test\validate_csv\input\resp_sample_raster.csv"


# 3. please provide result directory path:
#   attention: Please do not use the original batch directory path or projected directory path
output_directory = r"D:\pre_test\validate_csv\result"


################################################################################################
#                             4. Run
# Example:
# input:
#       main_csv_filepath = r"D:\results\main_sample_raster_arkids8.csv"
#       resp_csv_filepath = r"D:\results\main_sample_raster1.csv"
#       output_directory = r"D:\results"
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

output(f"*** starting 'checking csv files'")

if verify_setup([main_csv_filepath, resp_csv_filepath], [output_directory]):
    main_csv_headers = csv_headers(main_csv_filepath)
    validate_csv_files(main_csv_filepath, resp_csv_filepath, output_directory)
    output(f"*** end 'checking csv files'")