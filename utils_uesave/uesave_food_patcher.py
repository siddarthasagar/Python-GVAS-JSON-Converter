#!/usr/bin/env python3
"""
Safe patcher for Empires of the Undergrowth save files (uesave-rs workflow).
This version ensures only value changes, never structure changes.
"""

import json
import sys


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def patch_food_nodes(input_json, output_json, patch_template=None):
    print(f"📖 Loading save data from {input_json}")
    data = load_json(input_json)

    # Load or initialize patch list
    if patch_template:
        print(f"📋 Loading patch template from {patch_template}")
        patch = load_json(patch_template)
    else:
        print("⚠ No patch template provided, using default values")
        patch = []

    # Normalize patch to a list if a dict with numeric keys is provided
    if isinstance(patch, dict):
        patch = [patch[k] for k in sorted(patch) if isinstance(k, str) and k.isdigit()]

    # Locate resource nodes in either new (list) or old (dict) format
    def find_resource_nodes(data_obj):
        if isinstance(data_obj, list):
            for item in data_obj:
                if isinstance(item, dict) and item.get("name") == "ResourceBaseSaveStates":
                    return item.get("value", [])
            return []
        if isinstance(data_obj, dict):
            try:
                return data_obj["root"]["properties"]["ResourceBaseSaveStates_0"]["Array"]["Struct"]["value"]
            except Exception:
                return []
        return []

    resource_nodes = find_resource_nodes(data)

    # Apply patches
    def apply_patch_to_node(node, food_val):
        struct = node.get("Struct", {})
        if "SavedFoodHeld_0" in struct:
            struct["SavedFoodHeld_0"]["Int"] = food_val
            return True
        if "SavedFoodHeld" in node:
            node["SavedFoodHeld"] = food_val
            return True
        if "value" in node and isinstance(node["value"], dict) and "SavedFoodHeld" in node["value"]:
            node["value"]["SavedFoodHeld"] = food_val
            return True
        return False

    patched_count = 0
    if isinstance(resource_nodes, list) and isinstance(patch, list):
        for i, node in enumerate(resource_nodes):
            if not (patch and i < len(patch)):
                continue
            patch_node = patch[i]
            if not isinstance(patch_node, dict) or not patch_node.get("enabled", False):
                continue
            if apply_patch_to_node(node, patch_node.get("food_value")):
                patched_count += 1

    print(f"✅ Patched {patched_count} nodes from template.")
    save_json(output_json, data)
    print(f"💾 Patched save written to {output_json}")
    return True


def main():
    MIN_ARGS = 3
    if len(sys.argv) < MIN_ARGS:
        print("Usage: python3 bin/uesave_food_patcher.py <input_json> <output_json> [patch_template.json]")
        sys.exit(1)
    input_json = sys.argv[1]
    output_json = sys.argv[2]
    MIN_ARGS_WITH_TEMPLATE = 4
    patch_template = sys.argv[3] if len(sys.argv) >= MIN_ARGS_WITH_TEMPLATE else None
    success = patch_food_nodes(input_json, output_json, patch_template)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
