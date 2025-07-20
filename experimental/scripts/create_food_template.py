#!/usr/bin/env python3

import csv
import json
import os

def main():
    csv_file = "food_nodes_inventory.csv"
    output_file = "patches/food_nodes_template.json"
    os.makedirs("patches", exist_ok=True)
    nodes = []
    with open(csv_file, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            node = {
                "index": int(row["Index"]),
                "current_value": int(row["SavedFoodHeld"]) if row["SavedFoodHeld"] else 0,
                "new_value": int(row["SavedFoodHeld"]) if row["SavedFoodHeld"] else 0,
                "resource_type": row["ResourceType"],
                "on_tile_id": int(row["OnTileID"]) if row["OnTileID"] else None,
                "on_colony_id": int(row["OnTileColonyID"]) if row["OnTileColonyID"] else None,
                "enabled": False
            }
            nodes.append(node)
    template = {
        "description": "Food Nodes Patch Template. Set 'enabled': true and edit 'new_value' for nodes you want to patch.",
        "nodes": nodes
    }
    with open(output_file, "w") as f:
        json.dump(template, f, indent=2)
    print(f"Template written to {output_file}")

if __name__ == "__main__":
    main()
