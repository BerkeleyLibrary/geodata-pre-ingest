import os
import json
import csv
from shutil import rmtree
from pathlib import Path
import arcpy
import workspace_directory
import common_helper

def create_geoblacklight_files(main_csv_arkid_filepath, resp_csv_arkid_filepath):
    all_resp_rows = csv_rows(resp_csv_arkid_filepath)
    field_names = geoblacklight_field_names(main_csv_arkid_filepath)
    collection_dir_path = final_directory_path("ingestion_collection")
    ingestion_dir_path = final_directory_path("ingestion")
    with open(main_csv_arkid_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            arkid = common_helper.require_arkid(row)
            resp_rows = [
                resp_row for resp_row in all_resp_rows if arkid == resp_row.get("arkid")
            ]
            create_geoblacklight_file(
                row, resp_rows, field_names, ingestion_dir_path, collection_dir_path
            )


def common_geoblacklight_fields(row, resp_rows, field_names):
    json_data = {}
    add_from_main_row(json_data, row, field_names)
    add_from_main_row_rights(json_data, row)
    add_from_resp_rows(json_data, resp_rows)
    add_from_arkid(json_data, row)
    add_default(json_data)
    return json_data


def create_geoblacklight_file(
    row, resp_rows, field_names, ingestion_dir_path, collection_dir_path
):
    with_dataset = common_helper.has_dataset(row)
    parent_dir_path = ingestion_dir_path if with_dataset else collection_dir_path

    json_data = common_geoblacklight_fields(row, resp_rows, field_names)
    add_references(json_data, row, with_dataset)
    if with_dataset:
        add_boundary(json_data, row)

    file_path = geoblacklight_file_path(row, parent_dir_path)
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


def geoblacklight_file_path(row, parent_dir_path):
    arkid = row.get("arkid")
    metadata_directory_path = os.path.join(
        parent_dir_path, f"{ARK_PREFIX}{arkid}", "metadata"
    )
    os.makedirs(metadata_directory_path, exist_ok=True)
    return os.path.join(metadata_directory_path, "geoblacklight.json")


def final_directory_path(prefix):
    directory_path = os.path.join(workspace_directory.results_directory_path, f"{prefix}_files")
    ensure_empty_directory(directory_path)
    return directory_path


def ensure_empty_directory(pathname):
    directory = Path(pathname)
    directory.mkdir(parents=True, exist_ok=True)

    for item in directory.iterdir():
        if item.is_dir():
            rmtree(item)
        else:
            item.unlink()


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
        return {**HOSTS, **HOSTS_PUBLIC}
    elif access == "restricted":
        return {**HOSTS, **HOSTS_SECURE}
    else:
        txt = f"geofile: '{row.get('geofile')}':  incorrect value in  'dct_accessRights_s', value = {access}"
        common_helper.output(txt, 1)
        raise ValueError(txt)


# Replace the #{arkid} placeholder in the host and append the quoted filename
def ref_url(hosts, key, arkid, filename):
    return f"{hosts[key].replace('#{arkid}', arkid)}{filename_with_wq(filename)}"


def filename_with_wq(filename):
    wq = '"'
    return f"{filename}{wq}"


def add_references(json_data, row, with_dataset):
    arkid = row.get("arkid")
    hosts = ref_hosts(row)

    refs = []
    if with_dataset:
        refs = [
            hosts["wfs"],
            hosts["wms"],
            ref_url(hosts, "ISO139", arkid, "iso19139.xml"),
            ref_url(hosts, "download", arkid, "data.zip"),
        ]
    doc = ref_doc(row, hosts, arkid)
    if doc:
        refs.append(doc)

    if refs:
        json_data["dct_references_s"] = "{" + ",".join(refs) + "}"


def ref_doc(row, hosts, arkid):
    file_path = row.get("doc_zipfile_path")
    if file_path:
        if os.path.isfile(file_path):
            basename = os.path.basename(file_path)
            return ref_url(hosts, "doc", arkid, basename)
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

# Set up constant variables to class methods                                
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
ARK_PREFIX = "berkeley-ark28722-"
INSTITUTION = "University of California Berkeley"
GEOBLACKLGITH_VERSION = "Aardvark"

original_doc_base_url = (
    "https://spatial.lib.berkeley.edu/maps/berkeley-ark28722-#{arkid}/data/original/"
)

HOSTS = {
    "ISO139": '"http://www.isotc211.org/schemas/2005/gmd/":"https://spatial.lib.berkeley.edu/maps/berkeley-ark28722-#{arkid}/metadata/',
    "download": f'"http://schema.org/downloadUrl":"{original_doc_base_url}',
    "doc": f'"http://lccn.loc.gov/sh85035852":"{original_doc_base_url}'
}


HOSTS_PUBLIC = {
    "wfs": '"http://www.opengis.net/def/serviceType/ogc/wfs":"https://geoservices.lib.berkeley.edu/geoserver/public/wfs"',
    "wms": '"http://www.opengis.net/def/serviceType/ogc/wms":"https://geoservices.lib.berkeley.edu/geoserver/public/wms"'
}

HOSTS_SECURE = {
    "wfs": '"http://www.opengis.net/def/serviceType/ogc/wfs":"https://geoservices.lib.berkeley.edu/geoserver/restricted/wfs"',
    "wms": '"http://www.opengis.net/def/serviceType/ogc/wms":"https://geoservices.lib.berkeley.edu/geoserver/restricted/wms"'
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
    resp_csv_arkid_filepath = common_helper.csv_filepath('resp', True)
    main_csv_arkid_filepath = common_helper.csv_filepath('main', True)
    common_helper.verify_workspace_and_files([main_csv_arkid_filepath, resp_csv_arkid_filepath])
    
    create_geoblacklight_files(main_csv_arkid_filepath, resp_csv_arkid_filepath)
