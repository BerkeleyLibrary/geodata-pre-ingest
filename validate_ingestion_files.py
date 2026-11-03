import os
import json
from pathlib import Path
import jsonschema
from jsonschema import validate
import workspace_directory
import common_helper

def validate_files(dir_path):
    missing_filepaths = []
    if Path(dir_path).is_dir():
        for record in os.listdir(dir_path):
            if not os.path.isdir(os.path.join(dir_path, record)):
                continue
            package_path = os.path.join(dir_path, record, f"berkeley-ark28722-{record}")
            for relative in [
                os.path.join("data", "original", "data.zip"),
                os.path.join("metadata", "geoblacklight.json"),
                os.path.join("metadata", "iso19139.xml"),
            ]:
                file_path = os.path.join(package_path, relative)
                if not Path(file_path).is_file():
                    missing_filepaths.append(file_path)
            geoserver_path = os.path.join(package_path, "data", "geoserver")
            if not (os.path.isdir(geoserver_path) and os.listdir(geoserver_path)):
                missing_filepaths.append(geoserver_path)
    if missing_filepaths:
        common_helper.output("Below ingestion files not found: ", 1)
        for filepath in missing_filepaths:
            common_helper.output(filepath, 1)

def validate_geoblacklight_schema(dir_path, arrdvark_schema_file_path):
    if Path(dir_path).is_dir():
        schema = ""
        with open(arrdvark_schema_file_path, "r", encoding="utf-8") as s:
            schema = json.load(s)

        json_files = get_filepaths(dir_path, ".json")

        for json_file in json_files:
            data = ""
            with open(json_file, "r", encoding="utf-8") as d:
                data = json.load(d)
                validate_output(data, schema, json_file)

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

def run_tool():
    # 1. arrdvark json schema file
    arrdvark_schema_file_path = (
        r"C:\pre-ingestion-config\geoblacklight-schema-aardvark.json"
    )
    result_directory_path = workspace_directory.results_directory_path

    # 2. geofiles geoblackligt json file location
    geoblacklight_directory_path = os.path.join(
        result_directory_path, "ingestion_files"
    )

    # 3. collection geoblackligt json file location
    geoblacklight_collection_directory_path = os.path.join(
        result_directory_path, "ingestion_collection_files"
    )
    common_helper.verify_workspace_and_files([arrdvark_schema_file_path])

    validate_geoblacklight_schema(geoblacklight_directory_path, arrdvark_schema_file_path)
    validate_geoblacklight_schema(geoblacklight_collection_directory_path, arrdvark_schema_file_path)
    validate_files(geoblacklight_directory_path)