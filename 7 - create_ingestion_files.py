import os
import logging
from pathlib import Path
import csv
import zipfile
from shutil import copyfile, rmtree, copy2
import json


################################################################################################
#                             1. functions                                                     #
################################################################################################
def create_files():
    ingestion_dir_path = final_directory_path("ingestion")
    with open(main_csv_arkid_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            if row.get("gbl_resourceClass_sm").lower() != "collections":
                create_files_on_row(row, ingestion_dir_path)

# each subdirectory under ingestion_files has four files, which will be validated in next script
def add_gbl_fileSize_s():
    ingestion_file_dirpath = os.path.join(result_directory_path, "ingestion_files")
    for root, _, files in os.walk(ingestion_file_dirpath):
       for file in files:
            file_path = os.path.join(root, file)
            if file == "geoblacklight.json" and os.path.isfile(file_path):
                data_file_path = os.path.join(root, "data.zip")
                update_json_file(file_path,data_file_path)

def get_ogp_geoblakcligh_files():
    ogp_dir_path = final_directory_path("ogp")
    move_geoblacklight("ingestion_files", ogp_dir_path)
    move_geoblacklight("ingestion_collection_files", ogp_dir_path)

def final_directory_path(prefix):
    directory_path = os.path.join(result_directory_path, f"{prefix}_files")
    ensure_empty_directory(directory_path)
    return directory_path

def update_json_file(json_file_path,data_file_path):
    try:
        data = {}
        with open(json_file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
            file_size = get_file_size(data_file_path)
            data['gbl_fileSize_s'] = file_size

        save_pretty_json_file(json_file_path, data)
    except Exception as ex:
            print(f"Cannot update gbl_fileSizes, please check existing of files{json_file_path}; {data_file_path}; - {ex}")

def get_file_size(file_path):
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024.0 ** 2)
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
    from_dir_path = os.path.join(result_directory_path, dir_name)
    if os.path.exists(from_dir_path):
        for root, _, files in os.walk(from_dir_path):
            for file in files:
                if file == "geoblacklight.json":
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        relative_path = os.path.relpath(file_path, from_dir_path)
                        ogp_file_path = os.path.join(to_dir_path, relative_path)
                        os.makedirs(os.path.dirname(ogp_file_path), exist_ok=True)
                        copy2(file_path, ogp_file_path)

def create_files_on_row(row, ingestion_dir_path):
    geofile_path = row.get("geofile")
    projected_geofile_path = correlated_filepath(geofile_path)

    arkid = row.get("arkid")

    def create_ingestion_file():
        ingestion_path = arkid_directory_path(arkid, ingestion_dir_path)
        cp_file(projected_geofile_path, ingestion_path, "iso19139.xml")
        cp_file(
            projected_geofile_path,
            ingestion_path,
            "geoblacklight.json",
        )
        wrap_up_zip(projected_geofile_path, arkid, ingestion_path, "map")
        wrap_up_zip(geofile_path, arkid, ingestion_path, "data")

        doc_filepath = row.get("doc_zipfile_path")
        if doc_filepath:
            cp_document_file(doc_filepath, ingestion_path)

    create_ingestion_file()

def arkid_directory_path(arkid, directory_path):
    arkid_directory_path = os.path.join(directory_path, arkid)
    ensure_empty_directory(arkid_directory_path)
    return arkid_directory_path


# Check geofiles listed in main csv are from source batch dirctory
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
        log_raise_error(text)


def cp_document_file(docfile_path, arkid_directory_path):
    basename = os.path.basename(docfile_path)
    if Path(docfile_path).is_file():
        dest_filepath = os.path.join(arkid_directory_path, basename)
        copyfile(docfile_path, dest_filepath)

    else:
        text = f"missing document file: {docfile_path}"
        log_raise_error(text)


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
            print(f"please check:  {text}") if ext == ".prj" else log_raise_error(text)
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
        log_raise_error(text)


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


def log_raise_error(text):
    logging.info(text)
    raise ValueError(text)


def ensure_empty_directory(pathname):
    if Path(pathname).is_dir():
        rm_contents(pathname)
    else:
        os.makedirs(pathname)


################################################################################################
#                                 2. setup                                                    #
################################################################################################
# attention: needs to finalize extesions here
shp_exts = [".cpg", ".dbf", ".prj", ".sbn", ".sbx", ".shp", ".shx"]
tif_exts = [".tif", ".tfw", ".prj", ".tif.ovr"]
# [".tif", ".aux", ".tfw", ".prj", ".tif.ovr"]

# 1. setup log file path
logfile = r"C:\process_data\log\process.log"
logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format="%(message)s - %(asctime)s",
)

# 2. Please provide source data directory path,
#    make sure this is the source directory path from which main.csv file was generated.
source_batch_directory_path = r"C:\process_data\source_batch"

# 3. Please provide projected data directory path
projected_batch_directory_path = r"C:\process_data\source_batch_projected"


# 4. Please provide main csv file path which have been assigned with arkids
main_csv_arkid_filepath = r"C:\process_data\csv_files_arkid\main_arkid.csv"

# 5. please provide result directory path
result_directory_path = r"C:\process_data\results"


################################################################################################
#                             3. Create ingestion files
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
#  The geofile was assinged an arkid "a7gt36" in the main_csv_file.
# |---- a7gt36
# |------ data.zip
# |------ doc.zip
# |------ iso19139.xml
# |------ map.zip
# additional: 
# 1)  after creating data.zip file for each arkid related geofile, get data.zip file size, and update it to geoblacklight.json
# 2)  moving ingenstion geoblacklight.json and collection geoblacklight.json to OGP directory
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


script_name = "7 - create_ingestion_files.py"
output(f"***starting  {script_name}")

if verify_setup(
    [main_csv_arkid_filepath],
    [
        source_batch_directory_path,
        projected_batch_directory_path,
        result_directory_path,
    ],
):
    create_files()
    add_gbl_fileSize_s()
    get_ogp_geoblakcligh_files()
    output(f"***completed {script_name}")


