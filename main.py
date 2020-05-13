import json
import yaml
import sys
import os

from json_to_swagger import JsonToSwaggerConverter

if __name__ == '__main__':
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if len(args) == 0:
        raise SystemExit(f"Usage: {sys.argv[0]} <json-file-path> <RootEntityName> [swagger-file-path] [-v]")

    verbose = True if "-v" in opts else False

    json_file_path = fr'{args[0]}'
    root_entity = args[1] if len(args) > 1 else 'RootEntity'
    swagger_file_path = args[2] if len(args) > 2 else fr'{args[0].replace("json", "swagger")}.yaml'

    swagger_file_content = {}
    swagger_definitions = {}

    # opens the original swagger file
    if os.path.exists(swagger_file_path):
        with open(swagger_file_path) as swagger_file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            swagger_file_content = yaml.load(swagger_file, Loader=yaml.FullLoader)

            if not swagger_file_content:
                swagger_file_content = {}

            # gets the original definitions dict
            if 'definitions' in swagger_file_content:
                swagger_definitions = swagger_file_content['definitions']

    # creates the converter instance
    converter = JsonToSwaggerConverter(swagger_definitions, verbose)

    # opens the json file to generate new swagger definitions
    with open(json_file_path) as json_file:
        json_content = json.load(json_file)
        converter.convert(json_content, root_entity)
        swagger_file_content['definitions'] = converter.swagger_definitions

    # writes the new definitions to swagger file
    with open(swagger_file_path, 'w+') as newFile:
        yaml.dump(swagger_file_content, newFile, default_flow_style=False, sort_keys=False)
