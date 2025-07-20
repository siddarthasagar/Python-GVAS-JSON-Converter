#!/usr/bin/env python3

import json

def print_keys(obj, path="", depth=0, max_depth=6):
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
    print("\n=== First Resource Node ===")
    try:
        resource_nodes = props["ResourceBaseSaveStates_0"]["Array"]["Struct"]["value"]
        print_keys(resource_nodes[0], path="ResourceBaseSaveStates_0.Array.Struct.value[0]", depth=0, max_depth=5)
    except Exception as e:
        print(f"Could not inspect ResourceBaseSaveStates_0: {e}")
    print("\n=== First Player State ===")
    try:
        player_states = props["PlayersSaveStates_0"]["Array"]["Struct"]["value"]
        print_keys(player_states[0], path="PlayersSaveStates_0.Array.Struct.value[0]", depth=0, max_depth=5)
    except Exception as e:
        print(f"Could not inspect PlayersSaveStates_0: {e}")

if __name__ == "__main__":
    main()
