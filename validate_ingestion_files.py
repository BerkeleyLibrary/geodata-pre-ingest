import os
# import logging
import json
from pathlib import Path
import jsonschema
from jsonschema import validate
import workspace_directory
import common_helper


################################################################################################
#                             1. functions                                                      #
################################################################################################


def validate_files(dir_path):
    basenames = ["map.zip", "data.zip", "geoblacklight.json", "iso19139.xml"]
    missing_filepaths = []
    for root, dirs, files in os.walk(dir_path):
        for dir in dirs:
            for name in basenames:
                file_path = os.path.join(root, dir, name)
                if not Path(file_path).is_file():
                    missing_filepaths.append(file_path)
    if missing_filepaths:
        common_helper.output("Below ingestion files not found: ", 1)
        for filepath in missing_filepaths:
            common_helper.output(filepath, 1)


def validate_geoblacklight_schema(dir_path, arrdvark_schema_file_path):
    if Path(dir_path).is_dir():
        schema = ""
        with open(arrdvark_schema_file_path) as s:
            schema = json.load(s)

        json_files = get_filepaths(dir_path, ".json")

        for json_file in json_files:
            data = ""
            with open(json_file, "r", encoding="utf-8") as d:
                data = json.load(d)
                validate_output(data, schema, json_file)


# def file_paths(dir_path, ext):
#     return [
#         os.path.join(dirpath, filename)
#         for dirpath, dirs, filenames in os.walk(dir_path)
#         for filename in filenames
#         if filename.endswith(ext)
#     ]


def get_filepaths(directory, ext):
    paths = []
    for file in os.listdir(directory):
        if file.endswith(ext):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                paths.append(file_path)
    return paths


def validate_output(data, schema, json_file):
    try:
        v = jsonschema.Draft7Validator(schema)
        messages = []
        for error in sorted(v.iter_errors(data), key=str):
            messages.append(error.message)

        if messages:
            common_helper.output(f"Invalid fields in {json_file}:", 2)
            for message in messages:
                common_helper.output(message, 2)

        common_helper("\n")

    except jsonschema.ValidationError as e:
        common_helper.output(
            f"Geoblackschema error when validating {json_file} : error --  " + e.message, 2
        )
    except:
        common_helper.output(f"exception in validating {json_file}", 2)


################################################################################################
#                                 2. set up                                                    #
################################################################################################

# # 1. Please provide your local log file path
# logfile = r"C:\process_data\log\process.log"
# logging.basicConfig(
#     filename=logfile,
#     level=logging.INFO,
#     format="%(message)s - %(asctime)s - %(funcName)s - %(levelname)s",
# )
# # 1. arrdvark json schema file
# arrdvark_schema_file_path = (
#     r"C:\pre-ingestion-config\geoblacklight-schema-aardvark.json"
# )

# # 2. geofiles geoblackligt json file location
# geoblacklight_directory_path = r"C:\process_data\results\ingestion_files"

# # 3. collection geoblackligt json file location
# geoblacklight_collection_directory_path = (
#     r"C:\process_data\results\ingestion_collection_files"
# )


################################################################################################
#                                3. Run                                              #
################################################################################################
def run_tool():
    # 1. arrdvark json schema file
    arrdvark_schema_file_path = (
        r"C:\pre-ingestion-config\geoblacklight-schema-aardvark.json"
    )
    result_directory_path = workspace_directory.results_directory_path

    # 2. geofiles geoblackligt json file location
    geoblacklight_directory_path = fr"{result_directory_path}\ingestion_files"

    # 3. collection geoblackligt json file location
    geoblacklight_collection_directory_path = fr"{result_directory_path}\ingestion_collection_files"
    common_helper.verify_workspace_and_files([arrdvark_schema_file_path])

    validate_geoblacklight_schema(geoblacklight_directory_path, arrdvark_schema_file_path)
    validate_geoblacklight_schema(geoblacklight_collection_directory_path, arrdvark_schema_file_path)
    validate_files(geoblacklight_directory_path)


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


# script_name = "8 - validate_ingestion_files.py"
# output(f"***starting  {script_name}")

# if verify_setup(
#     [arrdvark_schema_file_path],
#     [geoblacklight_directory_path],
# ):
#     validate_geoblacklight_schema(geoblacklight_directory_path)
#     validate_geoblacklight_schema(geoblacklight_collection_directory_path)

#     validate_files(geoblacklight_directory_path)
#     output(f"***completed {script_name}")
