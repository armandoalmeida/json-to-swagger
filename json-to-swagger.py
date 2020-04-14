import re
import json
import yaml
import sys
import os
from pattern.en import pluralize, singularize

swagger_definitions = {}
pretty_print = False


def camel_case_split(text):
    """
    Separates the camel case text into words
    :param text: camel case text
    :return: words separated text
    """
    return " ".join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', text))


def to_camel_case(text: str):
    """
    Transforms the first letter in upper case
    :param text: json id
    :return: camel case text formatted
    """
    return text[:1].upper() + text[1:]


def print_depth(message, depth):
    """ Pretty print """
    if pretty_print:
        for d in range(depth):
            sys.stdout.write('-')
        print(f'- {message}')


def get_default_object_properties(swagger_ref):
    """
    Returns a default swagger object
    :param swagger_ref: name of the swagger entity
    :return: default swagger object
    """
    return {
        "type": "object",
        "title": camel_case_split(swagger_ref),
        "description": f"{camel_case_split(swagger_ref)} Entity"
    }


def get_object_type(obj_content):
    """
    Converts the python types into swagger types
    :param obj_content: content of a property
    :return: content type
    """
    switcher = {
        "str": "string",
        "int": "integer",
        "bool": "boolean",
        "float": "number",
        "NoneType": "string"
    }
    return switcher[type(obj_content).__name__]


def check_object(camel_key, depth):
    """
    Check if object exists in swagger definition
    :param depth: recursive depth
    :param camel_key: entity name
    """
    if camel_key not in swagger_definitions:
        print_depth(f'(xx) {camel_key} not found', depth)
        swagger_definitions[camel_key] = get_default_object_properties(camel_key)


def add_property(key, swagger_ref, prop_dict):
    """
    Adds new property to an swagger object
    :param key: property key
    :param swagger_ref: entity name
    :param prop_dict: property content
    """
    ref = swagger_definitions[swagger_ref]
    if 'properties' not in ref:
        ref['properties'] = {}

    if key not in ref['properties']:
        ref['properties'][key] = {}

    key_dict = ref['properties'][key]
    key_dict.update(prop_dict)
    ref['properties'][key] = key_dict


def recursive_read_json(json_content, depth, swagger_ref):
    """
    A recursive function responsible for reading the JSON content and generate swagger definition (dict)
    :param json_content: json dict
    :param depth: recursive depth
    :param swagger_ref: entity name
    """
    if depth == 0:
        check_object(swagger_ref, depth)

    for key in json_content:
        camel_key = to_camel_case(key)
        obj_content = json_content[key]

        if type(obj_content) is dict:
            add_property(key, swagger_ref, {
                "$ref": f"#/definitions/{camel_key}"
            })

            check_object(camel_key, depth)

            print_depth(f'{camel_key}: {swagger_definitions[camel_key]}', depth)
            recursive_read_json(obj_content, depth + 1, camel_key)
            continue

        if type(obj_content) is list:
            camel_key = singularize(camel_key)
            add_property(key, swagger_ref, {
                "type": "array",
                "items": {
                    "$ref": f"#/definitions/{camel_key}"
                }
            })

            for obj in obj_content:
                check_object(camel_key, depth)
                recursive_read_json(obj, depth + 1, camel_key)
                # 'obj for' continue, it uses only the first item of array
                continue
            # 'key for' continue
            continue

        print_depth(f'{swagger_ref}.{key}: {obj_content}', depth)
        if swagger_ref in swagger_definitions:
            add_property(key, swagger_ref, {
                "type": get_object_type(obj_content),
                "example": obj_content
            })


if __name__ == '__main__':
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
    args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]

    if "-v" in opts:
        pretty_print = True

    if len(args) == 0:
        raise SystemExit(f"Usage: {sys.argv[0]} <json-file-path> <RootEntityName> [swagger-file-path] [-v]")

    json_file_path = fr'{args[0]}'
    root_entity = args[1] if len(args) > 1 else 'RootEntity'
    swagger_file_path = args[2] if len(args) > 2 else fr'{args[0].replace("json", "swagger")}.yaml'

    swagger_file_content = {}

    # opens the original swagger file
    if os.path.exists(swagger_file_path):
        with open(swagger_file_path) as swaggerFile:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python the dictionary format
            swagger_file_content = yaml.load(swaggerFile, Loader=yaml.FullLoader)

            if not swagger_file_content:
                swagger_file_content = {}

            # gets the original definitions dict
            if 'definitions' in swagger_file_content:
                swagger_definitions = swagger_file_content['definitions']

    # opens the json file to generate new swagger definitions
    with open(json_file_path) as jsonFile:
        jsonContent = json.load(jsonFile)
        recursive_read_json(jsonContent, 0, root_entity)
        swagger_file_content['definitions'] = swagger_definitions

    # writes the new definitions to swagger file
    with open(swagger_file_path, 'w+') as newFile:
        yaml.dump(swagger_file_content, newFile, default_flow_style=False, sort_keys=False)
