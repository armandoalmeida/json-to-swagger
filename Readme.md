# "Json to Swagger" conversor

Python utility created to convert JSON to Swagger definitions structure, based on entities concept.

## Dependencies
* Python 3.6+
* Libraries:
  * swagger-parser
  * pyyaml
  * pattern

> **Note**: Before run, execute:
```bash 
$ pip install -r requirements.txt
```

## Usage
Running:
```bash 
$ python main.py <json-file-path> <RootEntityName> [swagger-file-path] [-v]
```
* `json-file-path` - path of json file to convert
* `RootEntityName` - name of root swagger definitions entity
* `swagger-file-path` - path of swagger file. If the file has content, it will be merged with json converted content
* `-v` - verbose mode

*example.json*
```json 
{
   "id": "ffe74d36-4f76-4ca6-9dd1-8d5c9b16b056",
   "name": "JSON example",
   "description": "Just a simple JSON file to convert into swagger definition",
   "someObject": {
      "someInteger": 0,
      "someNumber": 0.1,
      "someBoolean": true,
      "someNull": null,
      "someString": "Example string content"
   },
   "items": [
      {
         "name": "Item",
         "subItem": {
            "subItemsOfSubItem": [
               {
                  "foo": "bar"
               }
            ]
         }
      }
   ]
}
```

*example.swagger.yaml*
```yaml 
definitions:
  Root:
    type: object
    title: Root
    description: Root Entity
    properties:
      id:
        type: string
        example: ffe74d36-4f76-4ca6-9dd1-8d5c9b16b056
      name:
        type: string
        example: JSON example
      description:
        type: string
        example: Just a simple JSON file to convert into swagger definition
      someObject:
        $ref: '#/definitions/SomeObject'
      items:
        type: array
        items:
          $ref: '#/definitions/Item'
  SomeObject:
    type: object
    title: Some Object
    description: Some Object Entity
    properties:
      someInteger:
        type: integer
        example: 0
      someNumber:
        type: number
        example: 0.1
      someBoolean:
        type: boolean
        example: true
      someNull:
        type: string
        example: null
      someString:
        type: string
        example: Example string content
  Item:
    type: object
    title: Item
    description: Item Entity
    properties:
      name:
        type: string
        example: Item
      subItem:
        $ref: '#/definitions/SubItem'
  SubItem:
    type: object
    title: Sub Item
    description: Sub Item Entity
    properties:
      subItemsOfSubItem:
        type: array
        items:
          $ref: '#/definitions/SubItemsOfSubItem'
  SubItemsOfSubItem:
    type: object
    title: Sub Items Of Sub Item
    description: Sub Items Of Sub Item Entity
    properties:
      foo:
        type: string
        example: bar

```

## Attention: Properties with same name will be merged

### Example
In the JSON structure bellow, it has the "items" property in two objects: 

```json 
{
   "items": [
      {
         "name": "Item",
         "subItem": {
            "items": [
               {
                  "foo": "bar"
               }
            ]
         }
      }
   ]
}
```

The result will merge the two "items" properties into "Item" entity:
```yaml 
definitions:
  RootEntity:
    type: object
    title: Root
    description: Root Entity
    properties:
      items:
        type: array
        items:
          $ref: '#/definitions/Item'
  Item:
    type: object
    title: Item
    description: Item Entity
    properties:
      name:
        type: string
        example: Item
      subItem:
        $ref: '#/definitions/SubItem'
      foo:
        type: string
        example: bar
  SubItem:
    type: object
    title: Sub Item
    description: Sub Item Entity
    properties:
      items:
        type: array
        items:
          $ref: '#/definitions/Item'

```
