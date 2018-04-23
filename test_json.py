import os
import logging
import json
import anyconfig
import jsonschema


if __name__ == '__main__':
    #conf1 = anyconfig.load(os.path.join(os.getcwd(), "config", "base-usb-test.json"),
    #                       ac_schema=os.path.join(os.getcwd(), "config-spec", "test-schema.json"))
    #conf1 = anyconfig.load(os.path.join(os.getcwd(), "config", "test.json"))
    #conf1 = anyconfig.load(os.path.join(os.getcwd(), "config", "sample.json"))
                           #ac_schema=os.path.join(os.getcwd(), "config-spec", "sample-schema.json"))
    #conf1 = anyconfig.load(os.path.join(os.getcwd(), "config", "base-usb-test.json"))
    #conf1 = anyconfig.load(os.path.join(os.getcwd(), "config", "base-usb-test.json"))
    #print conf1
    #schema1 = anyconfig.load(os.path.join(os.getcwd(), "config-spec", "test-schema.json"))
    #print schema1
    #(rc, err) = anyconfig.validate(conf1, schema1)
    #print rc, err

    temp_data = ''

    with open(os.path.join(os.getcwd(), "config", "base-usb-test.json"), 'r') as f:
        temp_data = f.read()

    json_data = json.loads(temp_data)

    with open(os.path.join(os.getcwd(), "config-spec", "test-schema.json"), 'r') as f:
        temp_data = f.read()

    json_schema = json.loads(temp_data)

    print json_data
    print json_schema

    print jsonschema.validate(json_data, json_schema)

    print json_data
