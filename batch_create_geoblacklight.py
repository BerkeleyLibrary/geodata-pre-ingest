import os
# import logging
import json
import csv
from shutil import rmtree
from pathlib import Path
import arcpy
import workspace_directory
import common_helper


################################################################################################
#                             1. functions                                                      #
################################################################################################
def create_geoblacklight_files(main_csv_arkid_filepath, resp_csv_arkid_filepath):
    all_resp_rows = csv_rows(resp_csv_arkid_filepath)
    field_names = geoblacklight_field_names(main_csv_arkid_filepath)
    with open(main_csv_arkid_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            arkid = row.get("arkid")
            if not arkid:
                text = f"Please check the main csv file: missing arkid in {row.get('geofile')}"
                common_helper.log_raise_error(text, 1)
            resp_rows = [
                resp_row for resp_row in all_resp_rows if arkid == resp_row.get("arkid")
            ]
            if has_dataset(row):
                create_geoblacklight_file_with_dataset(row, resp_rows, field_names)
            else:
                create_geoblacklight_file_without_dataset(row, resp_rows, field_names)


def has_dataset(row):
    geofile_path = row.get("geofile")
    return os.path.isfile(geofile_path)


def common_geoblacklight_fields(row, resp_rows, field_names):
    json_data = {}
    add_from_main_row(json_data, row, field_names)
    add_from_main_row_rights(json_data, row)
    add_from_resp_rows(json_data, resp_rows)
    add_from_arkid(json_data, row)
    add_default(json_data)
    return json_data


def create_geoblacklight_file_with_dataset(row, resp_rows, field_names):
    json_data = common_geoblacklight_fields(row, resp_rows, field_names)

    add_dataset_references(json_data, row)
    add_boundary(json_data, row)

    file_path = dataset_geoblacklight_file_path(row)
    save_pretty_json_file(file_path, json_data)


def create_geoblacklight_file_without_dataset(row, resp_rows, field_names):
    json_data = common_geoblacklight_fields(row, resp_rows, field_names)

    add_non_dataset_references(json_data, row)

    file_path = non_dataset_geoblacklight_file_path(row)
    save_pretty_json_file(file_path, json_data)


def proj_geofile_path(row):
    try:
        geofile_path = row.get("geofile")
        rel_geofile_name = os.path.relpath(geofile_path, workspace_directory.source_batch_directory_path)
        return os.path.join(workspace_directory.projected_batch_directory_path, rel_geofile_name)
    except Exception:
        txt = f"Could not find {proj_geofile_path}"
        common_helper.output(txt, 1)
        raise ValueError(txt)


def dataset_geoblacklight_file_path(row):
    projected_geofile_path = proj_geofile_path(row)
    base = os.path.splitext(projected_geofile_path)[0]
    return f"{base}_geoblacklight.json"


def non_dataset_geoblacklight_file_path(row):
    arkid = row.get("arkid")
    collection_dir_path = final_directory_path("ingestion_collection")
    arkid_directory_path = os.path.join(collection_dir_path, arkid)
    ensure_empty_directory(arkid_directory_path)
    return f"{arkid_directory_path}/geoblacklight.json"


def final_directory_path(prefix):
    directory_path = os.path.join(workspace_directory.results_directory_path, f"{prefix}_files")
    ensure_empty_directory(directory_path)
    return directory_path


def ensure_empty_directory(pathname):
    def rm_contents():
        for item in os.listdir(pathname):
            item_path = os.path.join(pathname, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                rmtree(item_path)

    if Path(pathname).is_dir():
        rm_contents()
    else:
        os.makedirs(pathname)


def save_pretty_json_file(file_path, json_data):
    with open(file_path, "w+", encoding="utf-8") as geo_json:
        geo_json.write(
            json.dumps(
                json_data,
                sort_keys=True,
                ensure_ascii=False,
                indent=4,
                separators=(",", ": "),
            )
        )


def add_from_main_row(json_data, row, field_names):
    def capitalize_first_letter(value):
        noCapWords = ["and", "is", "it", "or", "if"]
        words = value.split()
        capitalized_words = [
            word[0].upper() + word[1:]
            if (word not in noCapWords) and (word[0].isalpha())
            else word
            for word in words
        ]
        return " ".join(capitalized_words)

    def multiple_values(name, val):
        values = val.split("$")
        if name in RELATION_FIELDS:
            return [f"{PREFIX}-{val.strip()}" for val in values]
        if name == "dcat_theme_sm":
            return [ISOTOPIC[value.strip().zfill(3)] for value in values]
        if name in CAPITALIZED_FIELDS:
            return [capitalize_first_letter(value) for value in values]
        if name.endswith("im"):
            if name.endswith("drsim"):
                return [f"[{value}]" for value in values]
            else:
                try:
                    return [int(value) for value in values]
                except ValueError:
                    txt = f"{name} value is not a valid integer."
                    raise ValueError(txt)

        return values

    def single_value(name, val):
        if name == "dct_accessRights_s":
            return val.lower().capitalize()
        if name == "dct_issued_s":
            return val.replace('"', "").strip()
        if name.endswith("b"):
            if val.lower() == "true":
                return True
            elif val.lower() == "false":
                return False
            else:
                raise ValueError(f"{name} is neither 'true' nor 'false'")
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
    json_data["id"] = f"{PREFIX}-{arkid}"
    json_data["gbl_wxsIdentifier_s"] = arkid


def ref_hosts(row):
    access = row.get("dct_accessRights_s").strip().lower()
    if access == "public":
        return HOSTS
    elif access == "restricted":
        return HOSTS_SECURE
    else:
        txt = f"geofile: '{row.get('geofile')}':  incorrect value in  'dct_accessRights_s', value = {access}"
        common_helper.output(txt, 1)
        raise ValueError(txt)


def filename_with_wq(filename):
    wq = '"'
    return f"{filename}{wq}"


def add_dataset_references(json_data, row):
    arkid = row.get("arkid")
    id = f"{PREFIX}-{arkid}"
    hosts = ref_hosts(row)
    iso139 = f"{hosts['ISO139']}{id}/{filename_with_wq('iso19139.xml')}"
    download = f"{hosts['download']}{id}/{filename_with_wq('data.zip')}"
    content = f"{hosts['wfs']},{hosts['wms']},{iso139},{download}"
    doc = ref_doc(row, hosts, id)
    if doc:
        content = f"{content},{doc}"
    ref = "{" + content + "}"
    json_data["dct_references_s"] = ref.strip()


def add_non_dataset_references(json_data, row):
    arkid = row.get("arkid")
    id = f"{PREFIX}-{arkid}"
    hosts = ref_hosts(row)
    doc = ref_doc(row, hosts, id)
    if doc:
        json_data["dct_references_s"] = "{" + doc + "}"


def ref_doc(row, hosts, id):
    file_path = row.get("doc_zipfile_path")
    if file_path:
        if os.path.isfile(file_path):
            basename = os.path.basename(file_path)
            filename_doc = filename_with_wq(basename)
            return f"{hosts['doc']}{id}/{filename_doc}"
        else:
            txt = f"arkid: '{row.get('row_id')}': cannot find the document file {file_path} in 'doc_zipfile_path' column."
            raise ValueError(txt)
    return ""


def add_boundary(json_data, row):
    geofile = proj_geofile_path(row)

    def geotiff_boundary():
        try:
            raster = arcpy.Raster(geofile)
            W = raster.extent.XMin
            E = raster.extent.XMax
            N = raster.extent.YMax
            S = raster.extent.YMin
            return "ENVELOPE({0},{1},{2},{3})".format(W, E, N, S)
        except:
            txt = f"No boundary found: {geofile}"
            common_helper.output(txt, 1)
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
            txt = f"No boundary found: {geofile}"
            common_helper.output(txt, 1)
            raise ValueError

    if geofile.endswith(".shp"):
        boundary = shapefile_boundary()
        json_data["locn_geometry"] = boundary
        json_data["dcat_bbox"] = boundary

    if geofile.endswith(".tif"):
        boundary = geotiff_boundary()
        json_data["locn_geometry"] = boundary
        json_data["dcat_bbox"] = boundary


def csv_rows(csv_filepath):
    rows = []
    with open(csv_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            rows.append(row)
    return rows


# some columns in main csv file are only for ISO19139
def geoblacklight_field_names(csv_filepath):
    names = []
    with open(csv_filepath, "r", encoding="utf-8") as file:
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


# def log_raise_error(text):
#     logging.info(text)
#     raise ValueError(text)


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

PREFIX = "berkeley"
INSTITUTION = "University of California Berkeley"
GEOBLACKLGITH_VERSION = "Aardvark"

HOSTS = {
    "ISO139": '"http://www.isotc211.org/schemas/2005/gmd/":"https://spatial.lib.berkeley.edu/public/',
    "download": '"http://schema.org/downloadUrl":"https://spatial.lib.berkeley.edu/public/',
    "wfs": '"http://www.opengis.net/def/serviceType/ogc/wfs":"https://geoservices.lib.berkeley.edu/geoserver/wfs"',
    "wms": '"http://www.opengis.net/def/serviceType/ogc/wms":"https://geoservices.lib.berkeley.edu/geoserver/wms"',
    "doc": '"http://lccn.loc.gov/sh85035852":"https://spatial.lib.berkeley.edu/public/',
}

HOSTS_SECURE = {
    "ISO139": '"http://www.isotc211.org/schemas/2005/gmd/":"https://spatial.lib.berkeley.edu/metadata/',
    "download": '"http://schema.org/downloadUrl":"https://spatial.lib.berkeley.edu/UCB/',
    "wfs": '"http://www.opengis.net/def/serviceType/ogc/wfs":"https://geoservices-secure.lib.berkeley.edu/geoserver/wfs"',
    "wms": '"http://www.opengis.net/def/serviceType/ogc/wms":"https://geoservices-secure.lib.berkeley.edu/geoserver/wms"',
    "doc": '"http://lccn.loc.gov/sh85035852":"https://spatial.lib.berkeley.edu/metadata/',
}


CAPITALIZED_FIELDS = [
    "dct_spatial_sm",
    "dct_subject_sm",
    "gbl_resourceClass_sm",
    "gbl_resourceClass_sm",
]

# Combine three rights to "dct_rights_sm" in Geoblacklight
COMBINED_RIGHTS = ["rights_general", "rights_legal", "rights_security"]

EXCLUDING_FIELDS = [
    "rights_general",
    "rights_legal",
    "rights_security",
    "doc_zipfile_path",
    "summary",
]

RELATION_FIELDS = [
    "dct_isReplacedBy_sm",
    "dct_replaces_sm",
    "dct_isVersionOf_sm",
    "dct_source_sm",
    "dct_isPartOf_sm",
    "pcdm_memberOf_sm",
    "dct_relation_sm",
]

def run_tool():
    csv_files_arkid_directory_path = workspace_directory.csv_files_arkid_directory_path  
    resp_csv_arkid_filepath = common_helper.csv_filepath('resp', True)
    main_csv_arkid_filepath = common_helper.csv_filepath('main', True)
 
    common_helper.output(fr"*** Starting to create geoblacklight files to  {workspace_directory.projected_batch_directory_path}")
    common_helper.verify_workspace_and_files([main_csv_arkid_filepath, resp_csv_arkid_filepath])
    create_geoblacklight_files(main_csv_arkid_filepath, resp_csv_arkid_filepath)
    common_helper.output("*** Geoblacklight JSON files created successfully.", 0)


################################################################################################
#                                 3. set up                                                    #
################################################################################################

# # 1. setup log file path
# logfile = r"C:\process_data\log\process.log"
# logging.basicConfig(
#     filename=logfile,
#     level=logging.INFO,
#     format="%(message)s - %(asctime)s",
# )

# # 2. Source batch directory path
# source_batch_directory_path = r"C:\process_data\source_batch"

# # 3. Projected batch directory path
# projected_batch_directory_path = r"C:\process_data\source_batch_projected"

# # 4. please provide main csv and resp csv files here, check csv files in script "4 - check_csv_files.py", before running this script:
# main_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\main_arkid.csv"
# resp_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\resp_arkid.csv"

# # 5. please provide result directory path (the same as in "7 - create_ingestion_files.py")
# #    this script will save collection's geoblacklight json files to ruesult_driectory_path
# result_directory_path = r"C:\process_data\results"


################################################################################################
#                    4. Create a geoblacklight.json file for each  geofile                     #
################################################################################################
# def output(msg):
#     logging.info(msg)
#     print(msg)


# def verify_setup(file_paths, directory_paths):
#     verified = True
#     for file_path in file_paths:
#         if not Path(file_path).is_file():
#             print(f"{file_path} does not exit.")
#             verified = False

#     for directory_path in directory_paths:
#         if not Path(directory_path).is_dir():
#             print(f"{directory_path} does not exit.")
#             verified = False
#     return verified


# script_name = "6 - batch_create_geoblacklight.py"
# output(f"***starting  {script_name}")

# if verify_setup(
#     [logfile, main_csv_arkid_filepath, resp_csv_arkid_filepath],
#     [
#         projected_batch_directory_path,
#         source_batch_directory_path,
#         result_directory_path,
#     ],
# ):
#     create_geoblacklight_files()
#     output(f"***completed {script_name}")
