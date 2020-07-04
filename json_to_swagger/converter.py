import re
import sys
import yaml
import inflect


class Converter:
    swagger_definitions = {}
    verbose = False
    p = inflect.engine()

    def __init__(self, swagger_definitions=None, verbose=None):
        self.swagger_definitions = swagger_definitions if swagger_definitions else {}
        self.verbose = verbose if verbose else False

    @staticmethod
    def camel_case_split(text):
        """
        Separates the camel case text into words
        :param text: camel case text
        :return: words separated text
        """
        return " ".join(re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', text))

    @staticmethod
    def to_camel_case(text: str):
        """
        Transforms the first letter in upper case
        :param text: json id
        :return: camel case text formatted
        """
        return text[:1].upper() + text[1:]

    def print_depth(self, message, depth):
        """ Pretty print """
        if self.verbose:
            for d in range(depth):
                sys.stdout.write('-')
            print(f'- {message}')

    def get_default_object_properties(self, swagger_ref):
        """
        Returns a default swagger object
        :param swagger_ref: name of the swagger entity
        :return: default swagger object
        """
        return {
            "type": "object",
            "title": self.camel_case_split(swagger_ref),
            "description": f"{self.camel_case_split(swagger_ref)} Entity"
        }

    @staticmethod
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

    def check_object(self, camel_key, depth):
        """
        Check if object exists in swagger definition
        :param depth: recursive depth
        :param camel_key: entity name
        """
        if camel_key not in self.swagger_definitions:
            self.print_depth(f'(xx) {camel_key} not found', depth)
            self.swagger_definitions[camel_key] = self.get_default_object_properties(camel_key)

    def add_property(self, key, swagger_ref, prop_dict):
        """
        Adds new property to an swagger object
        :param key: property key
        :param swagger_ref: entity name
        :param prop_dict: property content
        """
        ref = self.swagger_definitions[swagger_ref]
        if 'properties' not in ref:
            ref['properties'] = {}

        if key not in ref['properties']:
            ref['properties'][key] = {}

        key_dict = ref['properties'][key]
        key_dict.update(prop_dict)
        ref['properties'][key] = key_dict

    def singularize(self, camel_key):
        """
        Returns the singular fo the camel key (one or more words)
        :param camel_key: entity name
        :return: singular of camel_key
        """
        words = self.camel_case_split(camel_key).split(" ")
        last_word = self.p.singular_noun(words[len(words) - 1])
        return "".join(words[1:len(words) - 2]) + last_word if last_word else camel_key

    def recursive_read_json(self, json_content, swagger_ref, depth=0):
        """
        A recursive function responsible for reading the JSON content and generate swagger definition (dict)
        :param json_content: json dict
        :param depth: recursive depth
        :param swagger_ref: entity name
        """
        if depth == 0:
            self.check_object(swagger_ref, depth)

        for key in json_content:
            camel_key = self.to_camel_case(key)
            obj_content = json_content[key]

            if type(obj_content) is dict:
                self.add_property(key, swagger_ref, {
                    "$ref": f"#/definitions/{camel_key}"
                })

                self.check_object(camel_key, depth)

                self.print_depth(f'{camel_key}: {self.swagger_definitions[camel_key]}', depth)
                self.recursive_read_json(obj_content, camel_key, depth + 1)
                continue

            if type(obj_content) is list:
                camel_key = self.singularize(camel_key)
                self.add_property(key, swagger_ref, {
                    "type": "array",
                    "items": {
                        "$ref": f"#/definitions/{camel_key}"
                    }
                })

                for obj in obj_content:
                    self.check_object(camel_key, depth)
                    self.recursive_read_json(obj, camel_key, depth + 1)
                # 'key for' continue
                continue

            self.print_depth(f'{swagger_ref}.{key}: {obj_content}', depth)
            if swagger_ref in self.swagger_definitions:
                self.add_property(key, swagger_ref, {
                    "type": self.get_object_type(obj_content),
                    "example": obj_content
                })

    def convert(self, json_content, root_entity="Root"):
        self.recursive_read_json(json_content, root_entity)
        return yaml.safe_dump(self.swagger_definitions, default_flow_style=False, sort_keys=False)
