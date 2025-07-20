#!/usr/bin/env python3
"""
Create a patch template for Empires of the Undergrowth saves.
- Identifies the latest stage save file (*StageN.sav).
- Copies the latest stage save file to a temporary directory.
- Converts the save to JSON (using uesave-rs).
- Extracts food node values from the JSON into a patch template.
- If no stage save is found, the script will exit with a warning.
"""

import os
import subprocess
import json
import re
import sys
import argparse

SAVE_DIR = os.path.expanduser("~/Library/Application Support/Epic/EotU/Saved/SaveGames")
TEMP_DIR = "temp"
PATCH_DIR = "patches"
PATCH_TEMPLATE_NUMERIC = os.path.join(PATCH_DIR, "jelly_territory_patch_template.json")
PATCH_TEMPLATE_FOOD = os.path.join(PATCH_DIR, "food_patch_template.json")

def find_main_saves():
    files = []
    for fname in os.listdir(SAVE_DIR):
        if fname.endswith(".sav") and not re.match(r".*-backup\d+\.sav$", fname):
            files.append(fname)
    return files

def find_latest_stage_save(main_saves):
    # Look for files with "Stage" and a number, pick the highest
    stage_files = []
    for fname in main_saves:
        match = re.search(r"Stage(\d+)", fname)
        if match:
            stage_num = int(match.group(1))
            stage_files.append((stage_num, fname))
    if stage_files:
        stage_files.sort(reverse=True)
        return stage_files[0][1]
    return None

def find_latest_leveldata_save(main_saves):
    # Find the latest Colony1LevelData.sav (or similar)
    leveldata_files = [fname for fname in main_saves if "Colony1LevelData" in fname]
    if not leveldata_files:
        return None
    # If multiple, pick the one with the latest mtime
    latest = max(leveldata_files, key=lambda f: os.path.getmtime(os.path.join(SAVE_DIR, f)))
    return latest

def copy_latest_saves(main_saves):
    os.makedirs(TEMP_DIR, exist_ok=True)
    for fname in main_saves:
        src = os.path.join(SAVE_DIR, fname)
        dst = os.path.join(TEMP_DIR, f"{fname}_ORIGINAL.sav")
        if os.path.exists(src):
            subprocess.run(["cp", src, dst])
            print(f"✓ Copied {src} -> {dst}")
        else:
            print(f"✗ Save not found: {src}")

def convert_to_json(main_saves):
    for fname in main_saves:
        src = os.path.join(TEMP_DIR, f"{fname}_ORIGINAL.sav")
        dst = os.path.join(TEMP_DIR, f"{fname}_working.json")
        if os.path.exists(src):
            subprocess.run(["uesave", "to-json", "--input", src, "--output", dst])
            print(f"✓ Converted {src} -> {dst}")
        else:
            print(f"✗ Backup not found: {src}")

def extract_food_nodes(latest_stage_save):
    os.makedirs(PATCH_DIR, exist_ok=True)
    print(f"Scanning {latest_stage_save} for food nodes...")
    json_path = os.path.join(TEMP_DIR, f"{latest_stage_save}_working.json")
    if not os.path.exists(json_path):
        print(f"✗ JSON not found: {json_path}")
        sys.exit(1)
    with open(json_path, "r") as f:
        data = json.load(f)
    # Try to find ResourceBaseSaveStates
    nodes = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("name") == "ResourceBaseSaveStates":
                nodes = item.get("value", [])
                break
    elif isinstance(data, dict):
        try:
            nodes = data["root"]["properties"]["ResourceBaseSaveStates_0"]["Array"]["Struct"]["value"]
        except Exception:
            nodes = []
    if not nodes:
        print(f"⚠ No food nodes found in {latest_stage_save}. Template will not be created.")
        return
    print(f"✓ Found {len(nodes)} food nodes in {latest_stage_save}")
    template = []
    for i, node in enumerate(nodes):
        food_val = None
        struct = node.get("Struct", {})
        if "SavedFoodHeld_0" in struct:
            food_val = struct["SavedFoodHeld_0"].get("Int")
        elif "SavedFoodHeld" in node:
            food_val = node["SavedFoodHeld"]
        elif "value" in node and isinstance(node["value"], dict) and "SavedFoodHeld" in node["value"]:
            food_val = node["value"]["SavedFoodHeld"]
        template.append({
            "enabled": True,
            "food_value": food_val,
            "description": f"{latest_stage_save} Node {i} (original value: {food_val})",
            "source_file": latest_stage_save,
            "node_index": i
        })
    with open(PATCH_TEMPLATE, "w") as f:
        json.dump(template, f, indent=2)
    print(f"✓ Patch template created: {PATCH_TEMPLATE}")

def _collect_int_values(obj, target_keys, found):
    """
    Recursively collect all 'Int' values for keys in target_keys.
    Example: If obj is {'RoyalJelly_0': {'Int': 123}}, finds 123.
    """
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in target_keys and isinstance(v, dict) and "Int" in v:
                found[k].append(v["Int"])
            _collect_int_values(v, target_keys, found)
    elif isinstance(obj, list):
        for item in obj:
            _collect_int_values(item, target_keys, found)

def extract_numeric_patch(latest_stage_save):
    os.makedirs(PATCH_DIR, exist_ok=True)
    print(f"Scanning {latest_stage_save} for RoyalJelly_0/Territory_0 values...")
    json_path = os.path.join(TEMP_DIR, f"{latest_stage_save}_working.json")
    if not os.path.exists(json_path):
        print(f"✗ JSON not found: {json_path}")
        sys.exit(1)
    with open(json_path, "r") as f:
        data = json.load(f)
    # Recursively search for RoyalJelly_0 and Territory_0 "Int" values
    found = {"RoyalJelly_0": [], "Territory_0": []}
    _collect_int_values(data, found.keys(), found)
    jelly_vals = found["RoyalJelly_0"]
    territory_vals = found["Territory_0"]
    if not jelly_vals and not territory_vals:
        print("Warning: Could not find RoyalJelly_0/Territory_0 Int values in save. Skipping numeric patch template creation.")
        return
    template = []
    for val in jelly_vals:
        template.append({
            "enabled": True,
            "resource": "jelly",
            "current_value": val,
            "new_value": None,
            "description": f"{latest_stage_save} RoyalJelly_0 (original value: {val})"
        })
    for val in territory_vals:
        template.append({
            "enabled": True,
            "resource": "territory",
            "current_value": val,
            "new_value": None,
            "description": f"{latest_stage_save} Territory_0 (original value: {val})"
        })
    with open(PATCH_TEMPLATE_NUMERIC, "w") as f:
        json.dump(template, f, indent=2)
    print(f"✓ Numeric patch template created: {PATCH_TEMPLATE_NUMERIC}")

def extract_food_patch(latest_stage_save):
    os.makedirs(PATCH_DIR, exist_ok=True)
    print(f"Scanning {latest_stage_save} for food nodes...")
    json_path = os.path.join(TEMP_DIR, f"{latest_stage_save}_working.json")
    if not os.path.exists(json_path):
        print(f"✗ JSON not found: {json_path}")
        sys.exit(1)
    with open(json_path, "r") as f:
        data = json.load(f)
    nodes = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("name") == "ResourceBaseSaveStates":
                nodes = item.get("value", [])
                break
    elif isinstance(data, dict):
        try:
            nodes = data["root"]["properties"]["ResourceBaseSaveStates_0"]["Array"]["Struct"]["value"]
        except Exception:
            nodes = []
    if not nodes:
        print(f"⚠ No food nodes found in {latest_stage_save}. Template will not be created.")
        return
    print(f"✓ Found {len(nodes)} food nodes in {latest_stage_save}")
    template = []
    for i, node in enumerate(nodes):
        food_val = None
        struct = node.get("Struct", {})
        if "SavedFoodHeld_0" in struct:
            food_val = struct["SavedFoodHeld_0"].get("Int")
        elif "SavedFoodHeld" in node:
            food_val = node["SavedFoodHeld"]
        elif "value" in node and isinstance(node["value"], dict) and "SavedFoodHeld" in node["value"]:
            food_val = node["value"]["SavedFoodHeld"]
        template.append({
            "enabled": True,
            "food_value": food_val,
            "new_value": None,
            "description": f"{latest_stage_save} Node {i} (original value: {food_val})",
            "source_file": latest_stage_save,
            "node_index": i
        })
    with open(PATCH_TEMPLATE_FOOD, "w") as f:
        json.dump(template, f, indent=2)
    print(f"✓ Food patch template created: {PATCH_TEMPLATE_FOOD}")

def main():
    parser = argparse.ArgumentParser(description="Create patch template for Empires of the Undergrowth saves.")
    parser.add_argument("--mode", choices=["numeric", "food"], required=True, help="Patch template mode")
    args = parser.parse_args()

    main_saves = find_main_saves()
    if not main_saves:
        print("No main save files found.")
        sys.exit(1)

    if args.mode == "numeric":
        latest_leveldata_save = find_latest_leveldata_save(main_saves)
        if not latest_leveldata_save:
            print("⚠ No Colony1LevelData.sav file found. Cannot create a numeric patch template.")
            sys.exit(1)
        print(f"Found latest Colony1LevelData save: {latest_leveldata_save}")
        saves_to_process = [latest_leveldata_save]
        copy_latest_saves(saves_to_process)
        convert_to_json(saves_to_process)
        extract_numeric_patch(latest_leveldata_save)
    elif args.mode == "food":
        latest_stage_save = find_latest_stage_save(main_saves)
        if not latest_stage_save:
            print("⚠ No stage save file (*StageN.sav) found. Cannot create a food patch template.")
            sys.exit(1)
        print(f"Found latest stage save: {latest_stage_save}")
        saves_to_process = [latest_stage_save]
        copy_latest_saves(saves_to_process)
        convert_to_json(saves_to_process)
        extract_food_patch(latest_stage_save)
    print("\nDone. Edit the patch template and run the appropriate make target.")

if __name__ == "__main__":
    main()
