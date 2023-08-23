import os
import logging
from pathlib import Path
import csv
import zipfile
from shutil import copyfile, rmtree


################################################################################################
#                             1. functions                                                     #
################################################################################################


def create_ingestion_files(
    result_directory_path,
    source_batch_path,
    projected_directory_path,
    main_csv_filepath,
):
    # verify_setup(
    #     main_csv_filepath,
    #     source_batch_path,
    #     projected_directory_path,
    #     result_directory_path,
    # )

    name = source_batch_path.split("\\")[-1]
    to_directory_path = os.path.join(result_directory_path, f"{name}_ingestion_files")
    ensure_dir_exists(to_directory_path)

    with open(main_csv_filepath, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            create_ingestion_files_on_row(
                row, source_batch_path, projected_directory_path, to_directory_path
            )


def create_ingestion_files_on_row(
    row,
    source_batch_path,
    projected_directory_path,
    to_directory_path,
):
    arkid = row["arkid"]
    arkid_directory_path = os.path.join(to_directory_path, arkid)
    ensure_new_content(arkid_directory_path)

    save_ingestion_files(
        arkid_directory_path, row, source_batch_path, projected_directory_path
    )


def save_ingestion_files(
    arkid_directory_path, row, source_batch_path, projected_directory_path
):
    geofile_path = row["geofile"]
    source_geofile_path = correlated_filepath(source_batch_path, geofile_path)
    projected_geofile_path = correlated_filepath(projected_directory_path, geofile_path)

    cp_iso19139(projected_geofile_path, arkid_directory_path)
    create_map_zip(projected_geofile_path, row["arkid"], arkid_directory_path)
    create_data_zip(source_geofile_path, arkid_directory_path)

    doc_filepath = row["doc_zipfile_path"]
    if doc_filepath:
        cp_document_file(doc_filepath, arkid_directory_path)


def correlated_filepath(directory, geofile_path):
    basename = os.path.basename(geofile_path)
    filepath = os.path.join(directory, basename)
    if Path(filepath).is_file():
        return filepath
    else:
        text = f"File {filepath} does not exist"
        log_raise_error(text)


# cannot use rmtree to remove directory,
# it will get writting permission errors after using rmtree to remove a directory
def rm_contents(directory_path):
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            rmtree(item_path)


def cp_iso19139(geofile_path, arkid_directory_path):
    base = os.path.splitext(geofile_path)[0]
    iso_19139_filepath = f"{base}_iso19139.xml"
    if Path(iso_19139_filepath).is_file():
        dest_filepath = os.path.join(arkid_directory_path, "iso_19139.xml")
        copyfile(iso_19139_filepath, dest_filepath)

    else:
        text = f"missing iso19139 file: {iso_19139_filepath}"
        log_raise_error(text)


def cp_document_file(docfile_path, arkid_directory_path):
    basename = os.path.basename(docfile_path)
    if Path(docfile_path).is_file():
        dest_filepath = os.path.join(arkid_directory_path, basename)
        copyfile(docfile_path, dest_filepath)

    else:
        text = f"missing document file: {docfile_path}"
        log_raise_error(text)


def map_sourcefiles(geofile_path, arkid):
    base = os.path.splitext(geofile_path)[0]
    dic = {}

    map_extestions = extenstions(geofile_path)
    for ext in map_extestions:
        source_file = f"{base}{ext}"
        if Path(source_file).is_file():
            dic[source_file] = f"{arkid}{ext}"
        else:
            text = f"missing projected file: {source_file}"
            log_raise_error(text)
    return dic


def data_sourcefiles(geofile_path):
    base = os.path.splitext(geofile_path)[0]
    parent_path = os.path.split(geofile_path)[0]
    dic = {}
    for root, _, files in os.walk(parent_path):
        for file in files:
            original_filepath = os.path.join(root, file)
            original_base = os.path.splitext(original_filepath)[0]
            if original_base == base:
                dic[original_filepath] = file
    return dic


def create_map_zip(geofile_path, arkid, arkid_directory_path):
    dic = map_sourcefiles(geofile_path, arkid)
    zip_filepath = os.path.join(arkid_directory_path, "map.zip")
    create_zipfile(dic, zip_filepath)


def create_data_zip(geofile_path, arkid_directory_path):
    dic = data_sourcefiles(geofile_path)
    if dic:
        zip_filepath = os.path.join(arkid_directory_path, "data.zip")
        create_zipfile(dic, zip_filepath)
    else:
        text = f"no source files: {geofile_path}"
        log_raise_error(text)


def create_zipfile(dic, zip_filepath):
    with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zf:
        for source, destination in dic.items():
            zf.write(source, destination)


def extenstions(geofile_path):
    ext = geofile_path.split(".")[-1].lower()
    dic = {
        "shp": [".cpg", ".dbf", ".prj", ".sbn", ".sbx", ".shp", ".shx"],
        "tif": [".tif", ".tfw", ".prj", ".tif.ovr"],
    }
    return dic[ext]


# def extenstions(geofile_path):
#     ext = geofile_path.split(".")[-1].lower()
#     dic = {
#         "shp": [".cpg", ".dbf", ".prj", ".sbn", ".sbx", ".shp", ".shx"],
#         "tif": [".tif", ".aux", ".tfw", ".prj", ".tif.ovr"],
#     }
#     return dic[ext]


def log_raise_error(text):
    logging.info(text)
    raise ValueError(text)


def ensure_dir_exists(pathname):
    if not Path(pathname).exists():
        os.mkdir(pathname)


def ensure_new_content(pathname):
    if Path(pathname).is_dir():
        rm_contents(pathname)
    else:
        os.makedirs(pathname)


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

# 2. Please provide source data directory path here
source_batch_path = r"D:\from_susan\sample_raster"

# 3. Please provide projected data directory path here
projected_directory_path = r"D:\from_susan\sample_raster"

# 4. Please provide main csv file path which have been assigned with arkids
main_csv_filepath = r"D:\results\main_sample_raster_arkids3.csv"

# 5. please provide result directory path
#   attention: Please do not use the original batch directory path or projected directory path
#              Suggest to provide a specific directory path for result files
result_directory_path = r"D:\results"


################################################################################################
#                             3. Create ingestion files
#  Based on input:
#  source_batch_path = r"D:\from_susan\sample_raster"
#  projected_directory_path = r"D:\from_susan\sample_raster"
#  result_directory_path = r"D:\results"
#
#  Ingestion files will be created under below directory
#      "D:\results\sample_raster_ingestion_files"
#  Then in Windows explore, you can make a zip file from above directory for ingestion tool
#
#  Under above directory, each Geofile(shapefile or GeoTIFF) will have a subdirectory
#  with all related ingestion files. Below is an example of a subdirectory.
#  The geofile was assinged an arkid "a7gt36" in the main_csv_file.
# |---- a7gt36
# |------ data.zip
# |------ docs:
# |-------- fake1.pdf
# |-------- fake2.pdf
# |------ iso19139.xml
# |------ map.zip
################################################################################################
def output(msg):
    logging.info(msg)
    print(msg)


def verify_setup(main_csv_filepath, *args):
    verified = True
    for arg in args:
        if not Path(arg).is_dir():
            print(f"{arg} does not exit.")
            verified = False

    if not Path(main_csv_filepath).is_file():
        print(f"{main_csv_filepath} does not exit.")
        verified = False
    return verified


output(f"*** starting 'creating ingestion files'")

if verify_setup(
    main_csv_filepath,
    source_batch_path,
    projected_directory_path,
    result_directory_path,
):
    create_ingestion_files(
        result_directory_path,
        source_batch_path,
        projected_directory_path,
        main_csv_filepath,
    )

    output(f"*** end 'creating ingestion files'")