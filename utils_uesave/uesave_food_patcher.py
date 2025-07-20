#!/usr/bin/env python3
"""
Safe patcher for Empires of the Undergrowth save files (uesave-rs workflow).
This version ensures only value changes, never structure changes.
"""

import json
import sys
import os

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def patch_food_nodes(input_json, output_json, patch_template=None):
    print(f"📖 Loading save data from {input_json}")
    data = load_json(input_json)

    if patch_template:
        print(f"📋 Loading patch template from {patch_template}")
        patch = load_json(patch_template)
    else:
        print("⚠ No patch template provided, using default values")
        patch = []

    # Find ResourceBaseSaveStates in the save data
    resource_nodes = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("name") == "ResourceBaseSaveStates":
                resource_nodes = item.get("value", [])
                break
    elif isinstance(data, dict):
        # Old format fallback
        try:
            resource_nodes = data["root"]["properties"]["ResourceBaseSaveStates_0"]["Array"]["Struct"]["value"]
        except Exception:
            resource_nodes = []

    # Patch food nodes using the template
    patched_count = 0
    # Patch can be either a list or a dict with integer keys (from some JSON writers)
    if isinstance(patch, dict):
        # Convert dict with integer keys to list, skip non-integer keys
        patch_list = []
        for k in sorted(patch, key=lambda x: int(x) if x.isdigit() else float('inf')):
            if k.isdigit():
                patch_list.append(patch[k])
        patch = patch_list

    for i, node in enumerate(resource_nodes):
        # Patch only if template has a value for this node
        if patch and i < len(patch):
            patch_node = patch[i]
            # Defensive: skip if patch_node is not dict
            if not isinstance(patch_node, dict):
                continue
            # Only patch enabled nodes
            if patch_node.get("enabled", False):
                food_val = patch_node.get("food_value")
                # Try to patch SavedFoodHeld in various locations
                struct = node.get("Struct", {})
                if "SavedFoodHeld_0" in struct:
                    struct["SavedFoodHeld_0"]["Int"] = food_val
                    patched_count += 1
                elif "SavedFoodHeld" in node:
                    node["SavedFoodHeld"] = food_val
                    patched_count += 1
                elif "value" in node and isinstance(node["value"], dict) and "SavedFoodHeld" in node["value"]:
                    node["value"]["SavedFoodHeld"] = food_val
                    patched_count += 1
                # Add more patching logic here if needed

    print(f"✅ Patched {patched_count} nodes from template.")
    save_json(output_json, data)
    print(f"💾 Patched save written to {output_json}")
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 bin/uesave_food_patcher.py <input_json> <output_json> [patch_template.json]")
        sys.exit(1)
    input_json = sys.argv[1]
    output_json = sys.argv[2]
    patch_template = sys.argv[3] if len(sys.argv) > 3 else None
    success = patch_food_nodes(input_json, output_json, patch_template)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
