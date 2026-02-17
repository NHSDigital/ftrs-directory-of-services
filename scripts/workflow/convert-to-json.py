#!/usr/bin/env python3

import sys
import os
import json


def convert_to_json(proxygen_configuration):
    try:
        proxygen_configuration_json = json.loads(proxygen_configuration)

        return proxygen_configuration_json

    except Exception as e:
        print(f"Error converting Proxygen configuration to JSON: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    proxygen_configuration = os.environ.get('PROXYGEN_CONFIGURATION')

    proxygen_configuration_json = convert_to_json(proxygen_configuration)
    print(proxygen_configuration_json)
