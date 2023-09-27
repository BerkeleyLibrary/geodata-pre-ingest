import os
import logging
import json
import csv
from datetime import date
from pathlib import Path
import arcpy


# TODO:
# 1) add multiple download from csv later
# 2) check time fields
################################################################################################
#                             1. functions                                                      #
################################################################################################
def create_geoblacklight_files():
    resp_dic = csv_dic(resp_csv_filepath)
    field_names = geoblacklight_field_names(main_csv_filepath)
    with open(main_csv_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            arkid = row.get("arkid")
            if not arkid:
                text = f"Please check the main csv file: missing arkid in {row.get('geofile')}"
                log_raise_error(text)
            resp_rows = [
                resp_row for resp_row in resp_dic if arkid == resp_row["arkid"]
            ]
            create_geoblacklight_file(row, resp_rows, field_names)


def correlated_filepath(geofile_path):
    if not source_batch_directory_path in geofile_path:
        text = f"File '{geofile_path}' listed in main csv is not located in source batch directory: '{source_batch_directory_path}'"
        log_raise_error(text)

    filepath = geofile_path.replace(
        source_batch_directory_path, projected_batch_directory_path
    )
    if Path(filepath).is_file():
        return filepath
    else:
        text = f"File {filepath} does not exist"
        log_raise_error(text)


def geoblacklight_filepath(row):
    geofile_path = row.get("geofile")
    projected_geofile_path = correlated_filepath(geofile_path)
    base = os.path.splitext(projected_geofile_path)[0]
    return f"{base}_geoblacklight.json"


def create_geoblacklight_file(row, resp_rows, field_names):
    json_data = {}

    add_from_main_row(json_data, row, field_names)
    add_from_main_row_rights(json_data, row)
    add_from_resp_rows(json_data, resp_rows)
    add_from_arkid(json_data, row)
    add_default(json_data)

    file_path = geoblacklight_filepath(row)
    with open(file_path, "w+") as geo_json:
        geo_json.write(
            json.dumps(
                json_data,
                sort_keys=True,
                ensure_ascii=False,
                indent=4,
                separators=(",", ":"),
            )
        )


# todo: check time fields later
def add_from_main_row(json_data, row, field_names):
    def multiple_values(name, val):
        values = val.split("$")
        if name == "dcat_theme_sm":
            return [ISOTOPIC[value.strip().zfill(3)] for value in values]
        if name in CAPITALIZED_FIELDS:
            return [value.title() for value in values]
        return values

    def single_value(name, val):
        if name == "dct_accessRights_s":
            return val.lower().capitalize()
        if name == "dct_issued_s":
            return val.replace('"', "").strip()
        return val

    def add(name, value):
        final_value = (
            multiple_values(name, value)
            if name.endswith("m")
            else single_value(name, value)
        )
        json_data[name] = final_value

    for name in field_names:
        value = current_val(name, row)
        if value:
            add(name, value)


def current_val(name, row):
    value = row.get(name)
    value_o = row.get(f"{name}_o")
    return value_o if value_o and (not value) else value


def add_from_main_row_rights(json_data, row):
    rights = []
    for name in COMBINED_RIGHTS:
        value = current_val(name, row)
        if value:
            rights.extend(value.split("$"))
    if rights:
        json_data["dct_rights_sm"] = rights


def add_from_resp_rows(json_data, rows):
    originators = resp_names(rows, "006")
    publishers = resp_names(rows, "010")
    owners = resp_names(rows, "003")

    if originators:
        json_data["dct_creator_sm"] = originators
    if publishers:
        json_data["dct_publisher_sm"] = publishers
    if owners:
        json_data["dct_rightsHolder_sm"] = owners


def add_default(json_data):
    json_data["schema_provider_s"] = INSTITUTION
    json_data["gbl_mdVersion_s"] = GEOBLACKLGITH_VERSION


def add_from_arkid(json_data, row):
    arkid = row.get("arkid")
    id = f"{PREFIX}{arkid}"
    access = row.get("dct_accessRights_s").strip().lower()

    def dc_references():
        hosts = HOSTS if access == "public" else HOSTS_SECURE
        iso_139_xml = f"{hosts['ISO139']}{id}/iso19139.xml"
        ref = (
            "{"
            + hosts["wfs"]
            + hosts["wms"]
            + iso_139_xml
            + hosts["download"]
            + id
            + '/data.zip"}'
        )
        return ref.strip()

    json_data["id"] = id
    json_data["gbl_wxsIdentifier_s"] = arkid
    json_data["dct_references_s"] = dc_references()


def add_boundary(json_data, row):
    geofile = row.get("geofile").strip()

    def geotiff_boundary():
        try:
            raster = arcpy.Raster(geofile)
            W = raster.extent.XMin
            E = raster.extent.XMax
            N = raster.extent.YMax
            S = raster.extent.YMin
            return "ENVELOPE({0},{1},{2},{3})".format(W, E, N, S)
        except:
            print(f"No boundary found: {geofile}")
            raise ValueError

    def shapefile_boundary():
        try:
            extent = arcpy.Describe(geofile).extent
            W = extent.XMin
            E = extent.XMax
            N = extent.YMax
            S = extent.YMin
            return "ENVELOPE({0},{1},{2},{3})".format(W, E, N, S)
        except:
            print(f"No boundary found: {geofile}")
            raise ValueError

    if geofile.endswith(".shp"):
        json_data["locn_geometry"] = shapefile_boundary()
    if geofile.endswith(".tif"):
        json_data["locn_geometry"] = geotiff_boundary()


def csv_dic(csv_filepath):
    lines = (line for line in open(csv_filepath, "r", encoding="utf-8"))
    rows = (line.strip().split(",") for line in lines)
    header = next(rows)
    return [dict(zip(header, row)) for row in rows]


def geoblacklight_field_names(csv_filepath):
    names = []
    with open(csv_filepath, "r") as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)[3:]
        names = [h for h in headers if not h.endswith("_o")]
    return [n for n in names if not n in EXCLUDING_FIELDS]


def resp_names(rows, code):
    names = []
    for row in rows:
        role_code = row.get("role").strip().zfill(3)
        if role_code == code:
            o_name = row.get("organization")
            i_name = row.get("individual")
            if i_name:
                names.append(i_name)
            else:
                names.append(o_name)
    return [name.strip() for name in names if name]


def log_raise_error(text):
    logging.info(text)
    raise ValueError(text)


################################################################################################
#                    2. set constant variables to class methods                                #
################################################################################################

ISOTOPIC = {
    "001": "Farming",
    "002": "Biota",
    "003": "Boundaries",
    "004": "Climatology, Meteorology and Atmosphere",
    "005": "Economy",
    "006": "Elevation",
    "007": "Environment",
    "008": "Geoscientific Information",
    "009": "Health",
    "010": "Imagery and Base Maps",
    "011": "Intelligence and Military",
    "012": "Inland Waters",
    "013": "Location",
    "014": "Oceans",
    "015": "Planning and Cadastral",
    "016": "Society",
    "017": "Structure",
    "018": "Transportation",
    "019": "Utilities and Communication",
}

PREFIX = "berkeley-"
INSTITUTION = "Berkeley"
GEOBLACKLGITH_VERSION = "Aardvark"

HOSTS = {
    "geoserver_host": "geoservices.lib.berkeley.edu",
    "ISO139": '"http://www.isotc211.org/schemas/2005/gmd/":"https://spatial.lib.berkeley.edu/metadata/',
    "download": '"http://schema.org/downloadUrl":"https://spatial.lib.berkeley.edu/public/',
    "wfs": '"http://www.opengis.net/def/serviceType/ogc/wfs":"https://geoservices.lib.berkeley.edu/geoserver/wfs",',
    "wms": '"http://www.opengis.net/def/serviceType/ogc/wms":"https://geoservices.lib.berkeley.edu/geoserver/wms",',
}

HOSTS_SECURE = {
    "geoserver_host": "geoservices-secure.lib.berkeley.edu",
    "ISO139": '"http://www.isotc211.org/schemas/2005/gmd/":"https://spatial.lib.berkeley.edu/metadata/',
    "download": '"http://schema.org/downloadUrl":"https://spatial.lib.berkeley.edu/UCB/',
    "wfs": '"http://www.opengis.net/def/serviceType/ogc/wfs":"https://geoservices-secure.lib.berkeley.edu/geoserver/wfs",',
    "wms": '"http://www.opengis.net/def/serviceType/ogc/wms":"https://geoservices-secure.lib.berkeley.edu/geoserver/wms",',
}


CAPITALIZED_FIELDS = ["dct_spatial_sm", "dct_subject_sm"]

# Combine three rights to "dct_rights_sm" in Geoblacklight
COMBINED_RIGHTS = ["rights_general", "rights_legal", "rights_security"]

EXCLUDING_FIELDS = [
    "rights_general",
    "rights_legal",
    "rights_security",
    "doc_zipfile_path",
]


################################################################################################
#                                 3. set up                                                    #
################################################################################################

# 1. setup log file path
logfile = r"D:\Log\shpfile_projection.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 2. Source batch directory path
source_batch_directory_path = r"D:\from_susan\sample_raster"
# source_batch_directory_path = r"D:\pre_test\create_geoblacklight\sample_raster"

# 3. Projected batch directory path
projected_batch_directory_path = r"D:\pre_test\create_geoblacklight\sample_raster"

# 4. please provide main csv and resp csv files here, check csv files in script "4 - check_csv_files.py", before running this script:
main_csv_filepath = (
    r"D:\pre_test\create_geoblacklight\input\main_sample_raster_arkids2.csv"
)
resp_csv_filepath = (
    r"D:\pre_test\create_geoblacklight\input\resp_sample_raster_arkids2.csv"
)


################################################################################################
#                    4. Create a geoblacklight.json file for each  geofile                               #
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


output(f"*** starting 'batch_iso19139s'")

if verify_setup(
    [logfile, main_csv_filepath, resp_csv_filepath],
    [projected_batch_directory_path, source_batch_directory_path],
):
    create_geoblacklight_files()
    output(f"*** end 'batch_iso19139s'")
