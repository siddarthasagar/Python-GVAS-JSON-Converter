#!/usr/bin/env python3
"""
Validation script to compare uesave-rs workflow with the old Python-only workflow.
This helps ensure the new workflow produces equivalent results.
"""

import json
import sys
from pathlib import Path

def load_json_safe(path):
    """Load JSON file safely with error handling."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {path}: {e}")
        return None

def extract_food_nodes_old_format(data):
    """Extract food nodes from old Python converter format."""
    try:
        nodes = data["root"]["properties"]["ResourceBaseSaveStates_0"]["Array"]["Struct"]["value"]
        food_values = []
        for i, node in enumerate(nodes):
            if "Struct" in node and "SavedFoodHeld_0" in node["Struct"]:
                food_values.append({
                    "node_id": i,
                    "food_value": node["Struct"]["SavedFoodHeld_0"]["Int"]
                })
        return food_values
    except Exception as e:
        print(f"❌ Error extracting from old format: {e}")
        return []

def extract_food_nodes_uesave_format(data):
    """Extract food nodes from uesave-rs format."""
    try:
        # Find ResourceBaseSaveStates in the flat list
        for item in data:
            if (isinstance(item, dict) and 
                item.get("name") == "ResourceBaseSaveStates" and 
                "value" in item):
                nodes = item["value"]
                food_values = []
                for i, node in enumerate(nodes):
                    # Handle the uesave-rs nested structure
                    if isinstance(node, dict):
                        # Look for SavedFoodHeld in various possible locations
                        food_val = None
                        if "SavedFoodHeld" in node:
                            food_val = node["SavedFoodHeld"]
                        elif "value" in node and isinstance(node["value"], dict):
                            if "SavedFoodHeld" in node["value"]:
                                food_val = node["value"]["SavedFoodHeld"]
                        
                        if food_val is not None:
                            food_values.append({
                                "node_id": i,
                                "food_value": food_val
                            })
                return food_values
        return []
    except Exception as e:
        print(f"❌ Error extracting from uesave format: {e}")
        return []

def compare_workflows(old_json_path, uesave_json_path):
    """Compare food node data between old and new workflows."""
    print("🔍 Comparing workflow outputs...")
    
    # Load both files
    old_data = load_json_safe(old_json_path)
    uesave_data = load_json_safe(uesave_json_path)
    
    if not old_data or not uesave_data:
        return False
    
    # Extract food nodes from both formats
    old_food_nodes = extract_food_nodes_old_format(old_data)
    uesave_food_nodes = extract_food_nodes_uesave_format(uesave_data)
    
    print(f"📊 Old format: {len(old_food_nodes)} food nodes")
    print(f"📊 uesave format: {len(uesave_food_nodes)} food nodes")
    
    # Compare totals
    old_total = sum(node["food_value"] for node in old_food_nodes)
    uesave_total = sum(node["food_value"] for node in uesave_food_nodes)
    
    print(f"🍯 Old format total food: {old_total}")
    print(f"🍯 uesave format total food: {uesave_total}")
    
    if old_total == uesave_total:
        print("✅ Food totals match!")
        return True
    else:
        print("❌ Food totals don't match!")
        print(f"   Difference: {uesave_total - old_total}")
        return False

def validate_json_structure(json_path, expected_format="auto"):
    """Validate JSON structure and determine format."""
    data = load_json_safe(json_path)
    if not data:
        return False, "unknown"
    
    print(f"🔍 Validating {json_path}")
    
    # Detect format
    if isinstance(data, dict) and "root" in data and "header" in data:
        detected_format = "old_python"
        print("📝 Detected: Old Python converter format")
    elif isinstance(data, list):
        detected_format = "uesave"
        print("📝 Detected: uesave-rs format")
    else:
        detected_format = "unknown"
        print("❓ Unknown format")
    
    # Basic validation
    if detected_format == "old_python":
        try:
            rbs = data["root"]["properties"]["ResourceBaseSaveStates_0"]["Array"]["Struct"]["value"]
            print(f"✅ Found {len(rbs)} resource nodes")
            return True, detected_format
        except Exception as e:
            print(f"❌ Invalid old format: {e}")
            return False, detected_format
    
    elif detected_format == "uesave":
        resource_count = 0
        for item in data:
            if isinstance(item, dict) and item.get("name") == "ResourceBaseSaveStates":
                if "value" in item:
                    resource_count = len(item["value"])
                    break
        print(f"✅ Found {resource_count} resource nodes")
        return True, detected_format
    
    return False, detected_format

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 validate_uesave_workflow.py validate <old_format.json> <uesave_format.json>")
        print("  python3 validate_uesave_workflow.py check <json_file>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "validate" and len(sys.argv) >= 4:
        old_json = sys.argv[2]
        uesave_json = sys.argv[3]
        success = compare_workflows(old_json, uesave_json)
        sys.exit(0 if success else 1)
    
    elif command == "check" and len(sys.argv) >= 3:
        json_file = sys.argv[2]
        valid, format_type = validate_json_structure(json_file)
        print(f"📋 Result: {'✅ Valid' if valid else '❌ Invalid'} {format_type} format")
        sys.exit(0 if valid else 1)
    
    else:
        print("❌ Invalid command or insufficient arguments")
        sys.exit(1)

if __name__ == "__main__":
    main()
