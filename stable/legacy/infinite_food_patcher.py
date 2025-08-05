#!/usr/bin/env python3

import argparse
import json


def get_resource_nodes(data):
    """Find the dict with name 'ResourceBaseSaveStates' and return its value list."""
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("name") == "ResourceBaseSaveStates":
                return item["value"]
        raise Exception("No item with name 'ResourceBaseSaveStates' found.")
    elif isinstance(data, dict):
        # fallback for older structure
        rbs = data["root"]["properties"]["ResourceBaseSaveStates_0"]
        if isinstance(rbs, dict):
            return rbs["Array"]["Struct"]["value"]
        elif isinstance(rbs, list):
            return rbs
        else:
            raise Exception("Unknown ResourceBaseSaveStates_0 structure")
    else:
        raise Exception("Unknown top-level JSON structure.")


def patch_nodes(data, node_indices, new_value):
    nodes = get_resource_nodes(data)
    for idx in node_indices:
        if idx >= len(nodes):
            print(f"Warning: Node index {idx} out of range (max: {len(nodes) - 1})")
            continue
        node = nodes[idx]

        # Handle both dict and list node structures
        if isinstance(node, dict):
            struct = node.get("Struct", {})
        elif isinstance(node, list):
            # If node is a list, find the dict with the struct data
            struct = None
            for item in node:
                if isinstance(item, dict) and "Struct" in item:
                    struct = item["Struct"]
                    break
            if not struct:
                print(f"Warning: No Struct found in node {idx}")
                continue
        else:
            print(f"Warning: Node {idx} has unknown structure")
            continue

        rss = struct.get("ResourceSubSaveState_0", {}).get("Struct", {}).get("Struct", {})
        food = rss.get("SavedFoodHeld_0", {})
        if isinstance(food, dict):
            food["Int"] = new_value
    return data


def patch_from_template(data, template_path):
    with open(template_path) as f:
        template = json.load(f)
    nodes = get_resource_nodes(data)
    patched_count = 0
    for entry in template.get("nodes", []):
        if entry.get("enabled"):
            idx = entry["index"]
            new_value = entry["new_value"]

            if idx >= len(nodes):
                print(f"Warning: Node index {idx} out of range (max: {len(nodes) - 1})")
                continue

            node = nodes[idx]

            # Handle both dict and list node structures
            if isinstance(node, dict):
                struct = node.get("Struct", {})
            elif isinstance(node, list):
                # If node is a list, find the dict with the struct data
                struct = None
                for item in node:
                    if isinstance(item, dict) and "Struct" in item:
                        struct = item["Struct"]
                        break
                if not struct:
                    print(f"Warning: No Struct found in node {idx}")
                    continue
            else:
                print(f"Warning: Node {idx} has unknown structure")
                continue

            rss = struct.get("ResourceSubSaveState_0", {}).get("Struct", {}).get("Struct", {})
            food = rss.get("SavedFoodHeld_0", {})
            if isinstance(food, dict):
                food["Int"] = new_value
                patched_count += 1
    print(f"Patched {patched_count} nodes from template.")
    return data


def main():
    parser = argparse.ArgumentParser(description="Patch SavedFoodHeld for selected resource nodes.")
    parser.add_argument("--input", required=True, help="Input JSON save file")
    parser.add_argument("--output", required=True, help="Output JSON save file")
    parser.add_argument("--nodes", help="Comma-separated list of node indices to patch (e.g. 1,5,10)")
    parser.add_argument("--value", type=int, help="Value to set for SavedFoodHeld")
    parser.add_argument("--patch", help="JSON patch template file (overrides --nodes/--value)")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    if args.patch:
        patched_data = patch_from_template(data, args.patch)
    elif args.nodes and args.value is not None:
        node_indices = [int(x) for x in args.nodes.split(",")]
        patched_data = patch_nodes(data, node_indices, args.value)
    else:
        print("❌ Must specify either --patch or both --nodes and --value")
        return

    with open(args.output, "w") as f:
        json.dump(patched_data, f, indent=2)

    print(f"Patched save written to {args.output}")


if __name__ == "__main__":
    main()
