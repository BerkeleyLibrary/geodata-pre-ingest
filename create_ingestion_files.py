import os
from pathlib import Path
import csv
import zipfile
from shutil import copyfile, rmtree, copy2
import json
import common_helper
import workspace_directory

ARK_PREFIX = "berkeley-ark28722-"


def create_files(main_csv_arkid_filepath):
    # ingestion_files is created and filled with geoblacklight.json by batch_create_geoblacklight
    ingestion_dir_path = os.path.join(
        workspace_directory.results_directory_path, "ingestion_files"
    )
    os.makedirs(ingestion_dir_path, exist_ok=True)
    with open(main_csv_arkid_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            if has_dataset(row):
                create_files_on_row(row, ingestion_dir_path)


def has_dataset(row):
    geofile_path = row.get("geofile")
    return os.path.isfile(geofile_path)


# each subdirectory under ingestion_files has four files, which will be validated in next script
def add_gbl_fileSize_s():
    ingestion_file_dirpath = os.path.join(workspace_directory.results_directory_path, "ingestion_files")
    for root, _, files in os.walk(ingestion_file_dirpath):
        for file in files:
            file_path = os.path.join(root, file)
            if file == "geoblacklight.json" and os.path.isfile(file_path):
                # root is <ark dir>/metadata; data.zip is under data/original
                data_file_path = os.path.join(os.path.dirname(root), "data", "original", "data.zip")
                update_json_file(file_path, data_file_path)


def get_ogp_geoblakcligh_files():
    ogp_dir_path = final_directory_path("ogp")
    move_geoblacklight("ingestion_files", ogp_dir_path)
    move_geoblacklight("ingestion_collection_files", ogp_dir_path)


def final_directory_path(prefix):
    directory_path = os.path.join(workspace_directory.results_directory_path, f"{prefix}_files")
    ensure_empty_directory(directory_path)
    return directory_path


def update_json_file(json_file_path, data_file_path):
    try:
        data = {}
        with open(json_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            file_size = get_file_size(data_file_path)
            data["gbl_fileSize_s"] = f"{file_size} MB"

        save_pretty_json_file(json_file_path, data)
    except Exception as ex:
        msg =  f"Cannot update gbl_fileSizes, please check existing of files{json_file_path}; {data_file_path}; - {ex}"
        common_helper.output(msg, 1)

def get_file_size(file_path):
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024.0**2)
    size = round(file_size_mb, 2)
    return str(size)

def save_pretty_json_file(file_path, json_data):
    with open(file_path, "w+", encoding="utf-8") as geo_json:
        geo_json.write(
            json.dumps(
                json_data,
                sort_keys=True,
                ensure_ascii=False,
                indent=4,
                separators=(",", ":"),
            )
        )

def move_geoblacklight(dir_name, to_dir_path):
    from_dir_path = os.path.join(workspace_directory.results_directory_path, dir_name)
    if os.path.exists(from_dir_path):
        for root, _, files in os.walk(from_dir_path):
            for file in files:
                if file == "geoblacklight.json":
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        relative_path = os.path.relpath(file_path, from_dir_path)
                        # keep OGP layout <arkid>/geoblacklight.json
                        arkid = relative_path.split(os.sep)[0].removeprefix(ARK_PREFIX)
                        ogp_file_path = os.path.join(to_dir_path, arkid, file)
                        os.makedirs(os.path.dirname(ogp_file_path), exist_ok=True)
                        copy2(file_path, ogp_file_path)

# def create_files_on_row(row, ingestion_dir_path):
#     geofile_path = row.get("geofile")
#     projected_geofile_path = correlated_filepath(geofile_path)

#     arkid = row.get("arkid")

#     def create_ingestion_file():
#         package_path = os.path.join(ingestion_dir_path, f"{ARK_PREFIX}{arkid}")
#         original_path = os.path.join(package_path, "data", "original")
#         geoserver_path = os.path.join(package_path, "data", "geoserver")
#         metadata_path = os.path.join(package_path, "metadata")
#         for path in (original_path, geoserver_path, metadata_path):
#             os.makedirs(path, exist_ok=True)

#         cp_file(projected_geofile_path, metadata_path, "iso19139.xml")
#         cp_file(projected_geofile_path, metadata_path, "geoblacklight.json")
#         # former map.zip contents are placed directly in data/geoserver
#         for source, name in map_sourcefiles(projected_geofile_path, arkid).items():
#             copyfile(source, os.path.join(geoserver_path, name))
#         wrap_up_zip(geofile_path, arkid, original_path, "data")

#         doc_filepath = row.get("doc_zipfile_path")
#         if doc_filepath:
#             cp_document_file(doc_filepath, original_path)

#     create_ingestion_file()


def create_files_on_row(row, ingestion_dir_path):
    geofile_path = row.get("geofile")
    projected_geofile_path = correlated_filepath(geofile_path)

    arkid = row.get("arkid")

    def create_ingestion_file():
        package_path = os.path.join(ingestion_dir_path, f"{ARK_PREFIX}{arkid}")
        original_path = os.path.join(package_path, "data", "original")
        geoserver_path = os.path.join(package_path, "data", "geoserver")
        metadata_path = os.path.join(package_path, "metadata")
        for path in (original_path, geoserver_path, metadata_path):
            os.makedirs(path, exist_ok=True)

        cp_file(projected_geofile_path, metadata_path, "iso19139.xml")
        geoblacklight_path = os.path.join(metadata_path, "geoblacklight.json")
        if not Path(geoblacklight_path).is_file():
            common_helper.log_raise_error(f"missing file: {geoblacklight_path}")
        # former map.zip contents are placed directly in data/geoserver
        for source, name in map_sourcefiles(projected_geofile_path, arkid).items():
            copyfile(source, os.path.join(geoserver_path, name))
        wrap_up_zip(geofile_path, arkid, original_path, "data")

        doc_filepath = row.get("doc_zipfile_path")
        if doc_filepath:
            cp_document_file(doc_filepath, original_path)

    create_ingestion_file()


# Check geofiles listed in main csv are from source batch dirctory
def correlated_filepath(geofile_path):
    source_directory = os.path.abspath(workspace_directory.source_batch_directory_path)
    source_filepath = os.path.abspath(geofile_path)
    try:
        common_directory = os.path.commonpath([source_directory, source_filepath])
    except ValueError:
        common_directory = ""

    if os.path.normcase(common_directory) != os.path.normcase(source_directory):
        text = f"File '{geofile_path}' listed in main csv is not located in source batch directory: '{workspace_directory.source_batch_directory_path}'"
        common_helper.log_raise_error(text)

    relative_filepath = os.path.relpath(source_filepath, source_directory)
    filepath = os.path.join(
        workspace_directory.projected_batch_directory_path, relative_filepath
    )
    if Path(filepath).is_file():
        return filepath
    else:
        text = f"File {filepath} does not exist"
        common_helper.log_raise_error(text)


# cannot use rmtree to remove directories,
# it will get writting permission errors after using rmtree
def rm_contents(directory_path):
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            rmtree(item_path)


def cp_file(geofile_path, arkid_directory_path, name):
    base = os.path.splitext(geofile_path)[0]
    from_filepath = f"{base}_{name}"
    if Path(from_filepath).is_file():
        to_filepath = os.path.join(arkid_directory_path, name)
        copyfile(from_filepath, to_filepath)

    else:
        text = f"missing file: {from_filepath}"
        common_helper.log_raise_error(text)


def cp_document_file(docfile_path, arkid_directory_path):
    basename = os.path.basename(docfile_path)
    if Path(docfile_path).is_file():
        dest_filepath = os.path.join(arkid_directory_path, basename)
        copyfile(docfile_path, dest_filepath)

    else:
        text = f"missing document file: {docfile_path}"
        common_helper.log_raise_error(text)


# Example:
# geofile_path = r'D:\gtest\1950\1950prj_county.shp'
# base = "D:\test\1950\1950prj_county"
def map_sourcefiles(geofile_path, arkid):
    base = os.path.splitext(geofile_path)[0]
    dic = {}

    map_extestions = get_extensions(geofile_path)
    for ext in map_extestions:
        source_file = f"{base}{ext}"
        if Path(source_file).is_file():
            dic[source_file] = f"{arkid}{ext}"
        else:
            text = f"missing projected file: {source_file}"
            # give a warning: some projected GeoTIFF files from ArcGIS Pro don't include .prj file.
            #  Check this after ingesting GeoTIFF to geoserver instance
            common_helper.output(f"please check:  {text}") if ext == ".prj" else common_helper.log_raise_error(text)
    return dic


# Example:
# geofile_path = r'D:\gtest\1950\1950prj_county.shp'
# barename = "1950prj_county"
# parent_path = "D:\test\1950"
def data_sourcefiles(geofile_path):
    barename = Path(geofile_path).stem
    parent_path = os.path.split(geofile_path)[0]
    dic = {}
    for file in os.listdir(parent_path):
        name = Path(file).stem.split(".")[0]
        if name == barename:
            file_path = os.path.join(parent_path, file)
            if os.path.isfile(file_path):
                dic[file_path] = file
    return dic


def wrap_up_zip(geofile_path, arkid, arkid_directory_path, type):
    dic = {}
    if type == "map":
        dic = map_sourcefiles(geofile_path, arkid)
    if type == "data":
        dic = data_sourcefiles(geofile_path)
    if dic:
        # filename = f"{type}.zip"
        zip_filepath = os.path.join(arkid_directory_path, f"{type}.zip")
        create_zipfile(dic, zip_filepath)
    else:
        text = f"no source files: {geofile_path}"
        common_helper.log_raise_error(text)


def create_zipfile(dic, zip_filepath):
    with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zf:
        for source, destination in dic.items():
            zf.write(source, destination)


#  "tif": [".tif", ".aux", ".tfw", ".prj", ".tif.ovr"],
def get_extensions(geofile_path):
    ext = Path(geofile_path).suffix[1:].lower()
    dic = {
        "shp": shp_exts,
        "tif": tif_exts,
    }
    return dic.get(ext)

def ensure_empty_directory(pathname):
    if Path(pathname).is_dir():
        rm_contents(pathname)
    else:
        os.makedirs(pathname)

# attention: needs to finalize extesions here
shp_exts = [".cpg", ".dbf", ".prj", ".sbn", ".sbx", ".shp", ".shx"]
tif_exts = [".tif", ".tfw", ".prj", ".tif.ovr"]
# [".tif", ".aux", ".tfw", ".prj", ".tif.ovr"]

################################################################################################
#  Example to create ingestion files
#  Based on input:
#  source_batch_directory_path = r"C:\process_data\source_batch"
#  projected_batch_directory_path = r"C:\process_data\source_batch_projected"
#  main_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\main_arkid.csv"
#  result_directory_path = r"C:\process_data\results"
#
#  Ingestion files will be created under below directory
#      "C:\process_data\results\ingestion_files"
#  From above directory, each Geofile(shapefile or GeoTIFF) will have a subdirectory
#  with all related ingestion files. Below is an example of a subdirectory.
#  The geofile was assinged an arkid "s7b70z" in the main_csv_file.
# |--berkeley-ark28722-s7b70z
# |----data/original/data.zip
# |----data/original/doc.zip
# |----data/geoserver/s7b70z.shp
# |----data/geoserver/s7b70z.prj
# ...
# |----data/geoserver/s7b70z.*
# |----metadata/iso19139.xml
# |----metadata/geoblacklight.json
# additional:
# 1)  after creating data.zip file for each arkid related geofile, get data.zip file size, and update it to geoblacklight.json
# 2)  moving ingenstion geoblacklight.json and collection geoblacklight.json to OGP directory
################################################################################################
def run_tool(): 
    main_csv_arkid_filepath = common_helper.csv_filepath('main', True)
    common_helper.verify_workspace_and_files([main_csv_arkid_filepath])
   
    create_files(main_csv_arkid_filepath)
    add_gbl_fileSize_s()
    get_ogp_geoblakcligh_files()
