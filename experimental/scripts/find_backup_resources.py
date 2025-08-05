#!/usr/bin/env python3
"""
Find Resources value in uesave-rs converted backup JSON
"""

import json


def _search_resources_in_player(player) -> tuple[bool, object | None]:
    """Helper to extract Resources from a player dict; returns (found, value)."""
    if not isinstance(player, dict):
        return False, None

    player_props = player.get("properties")
    if not isinstance(player_props, dict):
        return False, None

    # Prefer direct key check
    if "Resources" in player_props:
        resources_prop = player_props["Resources"]
        if isinstance(resources_prop, dict) and "value" in resources_prop:
            return True, resources_prop["value"]
        return True, resources_prop

    # Fallback: scan for related keys to provide context
    for prop_name, prop_value in player_props.items():
        if prop_name == "Resources":
            return True, prop_value
    return False, None


def _recursive_search(obj, path=""):
    """Recursive fallback search for a 'Resources' key anywhere."""
    if isinstance(obj, dict):
        if "Resources" in obj:
            return obj["Resources"]
        for key, value in obj.items():
            found = _recursive_search(value, f"{path}.{key}")
            if found is not None:
                return found
    elif isinstance(obj, list):
        for j, item in enumerate(obj):
            found = _recursive_search(item, f"{path}[{j}]")
            if found is not None:
                return found
    return None


def find_resources_in_backup():
    """Find Resources value in the backup JSON file"""
    with open("test_backup.json") as f:
        data = json.load(f)

    print("🔍 SEARCHING FOR RESOURCES IN BACKUP FILE")
    print("=" * 50)

    # Navigate to PlayersSaveStates_0
    root = data.get("root", {})
    props = root.get("properties", {})
    player_states_key = "PlayersSaveStates_0"

    if player_states_key not in props:
        print("❌ PlayersSaveStates_0 not found")
        return None

    player_states = props[player_states_key]
    print(f"📊 PlayersSaveStates_0 structure: {type(player_states)}")

    result = None

    try:
        array_data = player_states["Array"]["Struct"]["value"]
        print(f"📊 Array value type: {type(array_data)}")

        if isinstance(array_data, list):
            print(f"📊 Found {len(array_data)} player save states")
            for i, player in enumerate(array_data):
                found, value = _search_resources_in_player(player)
                if found:
                    print(f"  ✅ Player {i} Resources: {value}")
                    result = value
                    break

        elif isinstance(array_data, dict):
            print(f"📊 Array data keys: {list(array_data.keys())}")
            if "Resources" in array_data:
                result = array_data["Resources"]
                print(f"✅ Found Resources: {result}")

    except KeyError as e:
        print(f"❌ KeyError navigating structure: {e}")
        print("\n🔍 Trying recursive search...")
        result = _recursive_search(player_states)

    if result is None:
        print("❌ Resources not found in backup file")
    return result


if __name__ == "__main__":
    find_resources_in_backup()
