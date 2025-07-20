#!/usr/bin/env python3

import json

def print_keys(obj, path="", depth=0, max_depth=4):
    if depth > max_depth:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{'  '*depth}{path}.{k} ({type(v).__name__})")
            print_keys(v, f"{path}.{k}", depth+1, max_depth)
    elif isinstance(obj, list):
        print(f"{'  '*depth}{path} [list of {len(obj)}]")
        if obj and depth < max_depth:
            print_keys(obj[0], f"{path}[0]", depth+1, max_depth)

def main():
    with open("test_backup.json", "r") as f:
        data = json.load(f)
    props = data["root"]["properties"]
    print("\n=== ResourceBaseSaveStates_0 ===")
    print_keys(props.get("ResourceBaseSaveStates_0", {}), path="ResourceBaseSaveStates_0", depth=0, max_depth=3)
    print("\n=== PlayersSaveStates_0 ===")
    print_keys(props.get("PlayersSaveStates_0", {}), path="PlayersSaveStates_0", depth=0, max_depth=3)

if __name__ == "__main__":
    main()
