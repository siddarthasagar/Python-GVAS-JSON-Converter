#!/usr/bin/env python3

import json

def extract_saved_foodheld(resource_nodes):
    """Sum all SavedFoodHeld_0.Int values in resource nodes."""
    total = 0
    for node in resource_nodes:
        struct = node.get("Struct", {})
        rss = struct.get("ResourceSubSaveState_0", {}).get("Struct", {}).get("Struct", {})
        food = rss.get("SavedFoodHeld_0", {}).get("Int")
        if isinstance(food, int):
            total += food
    return total

def extract_resources_value(player_states):
    """Extract Resources_0.Int from each player state (returns list of ints)."""
    values = []
    for player in player_states:
        struct = player.get("Struct", {})
        res = struct.get("Resources_0", {}).get("Int")
        if isinstance(res, int):
            values.append(res)
    return values

def analyze_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    try:
        resource_nodes = data["root"]["properties"]["ResourceBaseSaveStates_0"]["Array"]["Struct"]["value"]
    except Exception:
        resource_nodes = []
    try:
        player_states = data["root"]["properties"]["PlayersSaveStates_0"]["Array"]["Struct"]["value"]
    except Exception:
        player_states = []
    total_foodheld = extract_saved_foodheld(resource_nodes)
    resources_list = extract_resources_value(player_states)
    return total_foodheld, resources_list

def main():
    file1 = "test_backup.json"
    file2 = "test_backup2.json"
    print(f"Analyzing {file1} and {file2} ...\n")

    food1, reslist1 = analyze_file(file1)
    food2, reslist2 = analyze_file(file2)

    print(f"{file1}:")
    print(f"  Total SavedFoodHeld: {food1}")
    print(f"  Resources values:    {reslist1}")
    print()
    print(f"{file2}:")
    print(f"  Total SavedFoodHeld: {food2}")
    print(f"  Resources values:    {reslist2}")
    print()
    print("Difference (file2 - file1):")
    print(f"  ΔSavedFoodHeld: {food2 - food1}")
    if reslist1 and reslist2:
        for i, (r1, r2) in enumerate(zip(reslist1, reslist2)):
            print(f"  ΔResources (player {i}): {r2 - r1}")
    else:
        print("  ΔResources:     (could not extract)")

if __name__ == "__main__":
    main()
