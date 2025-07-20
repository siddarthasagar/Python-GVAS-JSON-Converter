#!/usr/bin/env python3
"""
Find Resources value in uesave-rs converted backup JSON
"""

import json

def find_resources_in_backup():
    """Find Resources value in the backup JSON file"""
    
    with open('test_backup.json', 'r') as f:
        data = json.load(f)
    
    print("🔍 SEARCHING FOR RESOURCES IN BACKUP FILE")
    print("=" * 50)
    
    # Navigate to PlayersSaveStates_0
    root = data.get('root', {})
    props = root.get('properties', {})
    
    if 'PlayersSaveStates_0' not in props:
        print("❌ PlayersSaveStates_0 not found")
        return
    
    player_states = props['PlayersSaveStates_0']
    print(f"📊 PlayersSaveStates_0 structure: {type(player_states)}")
    
    # Navigate through the structure
    try:
        # Get the array structure
        array_data = player_states['Array']['Struct']['value']
        print(f"📊 Array value type: {type(array_data)}")
        
        if isinstance(array_data, list):
            print(f"📊 Found {len(array_data)} player save states")
            
            for i, player in enumerate(array_data):
                if isinstance(player, dict):
                    print(f"\n🎮 Player {i} structure:")
                    print(f"  Keys: {list(player.keys())}")
                    
                    # Check for properties
                    if 'properties' in player:
                        player_props = player['properties']
                        if isinstance(player_props, dict):
                            print(f"  Properties: {list(player_props.keys())}")
                            
                            # Look for Resources
                            for prop_name, prop_value in player_props.items():
                                if prop_name == 'Resources':
                                    print(f"  ✅ Found Resources: {prop_value}")
                                    return prop_value
                                elif 'Resource' in prop_name:
                                    print(f"  📝 Found {prop_name}: {prop_value}")
                        
                        # Also check nested structure
                        if 'Resources' in player_props:
                            resources_prop = player_props['Resources']
                            if isinstance(resources_prop, dict):
                                print(f"  ✅ Found Resources (dict): {resources_prop}")
                                if 'value' in resources_prop:
                                    print(f"  ✅ Resources value: {resources_prop['value']}")
                                    return resources_prop['value']
                            else:
                                print(f"  ✅ Found Resources (direct): {resources_prop}")
                                return resources_prop
                    
        elif isinstance(array_data, dict):
            print(f"📊 Array data keys: {list(array_data.keys())}")
            
            # Look for Resources directly
            if 'Resources' in array_data:
                resources_value = array_data['Resources']
                print(f"✅ Found Resources: {resources_value}")
                return resources_value
                
    except KeyError as e:
        print(f"❌ KeyError navigating structure: {e}")
        
        # Try a different approach - search recursively
        def search_recursive(obj, path=""):
            if isinstance(obj, dict):
                if 'Resources' in obj:
                    print(f"✅ Found Resources at {path}: {obj['Resources']}")
                    return obj['Resources']
                for key, value in obj.items():
                    result = search_recursive(value, f"{path}.{key}")
                    if result is not None:
                        return result
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result = search_recursive(item, f"{path}[{i}]")
                    if result is not None:
                        return result
            return None
        
        print("\n🔍 Trying recursive search...")
        result = search_recursive(player_states)
        if result is not None:
            return result
    
    print("❌ Resources not found in backup file")
    return None

if __name__ == "__main__":
    find_resources_in_backup()
