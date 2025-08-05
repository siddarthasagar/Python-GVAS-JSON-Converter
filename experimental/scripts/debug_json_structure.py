#!/usr/bin/env python3

import json
import sys


def print_top_level_keys(data):
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                print(f"Item {i} keys: {list(item.keys())}")
                if "name" in item:
                    print(f"  name: {item['name']}")
                if "value" in item:
                    vtype = type(item["value"]).__name__
                    print(f"  value type: {vtype}")
                    if vtype == "list":
                        print(f"  value list len: {len(item['value'])}")
                    elif vtype == "dict":
                        print(f"  value dict keys: {list(item['value'].keys())}")
    elif isinstance(data, dict):
        print(f"Top-level dict keys: {list(data.keys())}")
    else:
        print(f"Top-level type: {type(data).__name__}")


def main():
    MIN_ARGS = 2  # script + json file
    if len(sys.argv) < MIN_ARGS:
        print("Usage: debug_json_structure.py <jsonfile>")
        return
    with open(sys.argv[1]) as f:
        data = json.load(f)
    print_top_level_keys(data)


if __name__ == "__main__":
    main()
