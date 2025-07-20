#!/usr/bin/env python3
"""
Differential Analysis Tool for Resources Calculation
Find the actual inputs that drive Resources calculation by comparing save states
"""

import json
import os
from pathlib import Path
from datetime import datetime
from SavConverter import read_sav, sav_to_json

def deep_diff(obj1, obj2, path=""):
    """
    Deep comparison of two objects to find differences
    Returns a list of differences with their paths
    """
    differences = []
    
    if type(obj1) != type(obj2):
        differences.append({
            'path': path,
            'type': 'type_change',
            'old_value': obj1,
            'new_value': obj2,
            'old_type': type(obj1).__name__,
            'new_type': type(obj2).__name__
        })
        return differences
    
    if isinstance(obj1, dict):
        # Check for added/removed keys
        keys1 = set(obj1.keys())
        keys2 = set(obj2.keys())
        
        for key in keys1 - keys2:
            differences.append({
                'path': f"{path}.{key}" if path else key,
                'type': 'removed',
                'old_value': obj1[key],
                'new_value': None
            })
        
        for key in keys2 - keys1:
            differences.append({
                'path': f"{path}.{key}" if path else key,
                'type': 'added',
                'old_value': None,
                'new_value': obj2[key]
            })
        
        # Check for changed values
        for key in keys1 & keys2:
            new_path = f"{path}.{key}" if path else key
            differences.extend(deep_diff(obj1[key], obj2[key], new_path))
    
    elif isinstance(obj1, list):
        # Compare list lengths first
        if len(obj1) != len(obj2):
            differences.append({
                'path': path,
                'type': 'length_change',
                'old_value': f"length: {len(obj1)}",
                'new_value': f"length: {len(obj2)}"
            })
        
        # Compare elements
        min_len = min(len(obj1), len(obj2))
        for i in range(min_len):
            new_path = f"{path}[{i}]"
            differences.extend(deep_diff(obj1[i], obj2[i], new_path))
        
        # Handle extra elements
        if len(obj1) > len(obj2):
            for i in range(len(obj2), len(obj1)):
                differences.append({
                    'path': f"{path}[{i}]",
                    'type': 'removed',
                    'old_value': obj1[i],
                    'new_value': None
                })
        elif len(obj2) > len(obj1):
            for i in range(len(obj1), len(obj2)):
                differences.append({
                    'path': f"{path}[{i}]",
                    'type': 'added',
                    'old_value': None,
                    'new_value': obj2[i]
                })
    
    elif obj1 != obj2:
        differences.append({
            'path': path,
            'type': 'value_change',
            'old_value': obj1,
            'new_value': obj2
        })
    
    return differences

def analyze_resource_inputs():
    """
    Analyze backup files to find what inputs drive Resources calculation
    """
    
    print("🔍 DIFFERENTIAL ANALYSIS: Finding Resources Calculation Inputs")
    print("=" * 80)
    
    backups_dir = Path('backups/EotU/SaveGames')
    backup_dirs = sorted([d for d in backups_dir.iterdir() if d.is_dir() and d.name != 'latest'])
    
    if len(backup_dirs) < 2:
        print("❌ Need at least 2 backup files for differential analysis")
        return
    
    # Load and convert all backup files
    backup_data = []
    for backup_dir in backup_dirs[:5]:  # Limit to first 5 for performance
        colony_file = backup_dir / 'Colony1LevelData.sav'
        if not colony_file.exists():
            continue
            
        try:
            print(f"📄 Loading {backup_dir.name}...")
            
            # Read the .sav file properly
            properties = read_sav(str(colony_file))
            
            # Convert to JSON string, then parse back to dict
            json_string = sav_to_json(properties, string=True)
            json_data = json.loads(json_string)
            
            # Extract Resources value for this backup
            resources_value = None
            for item in json_data:
                if item.get('name') == 'PlayersSaveStates':
                    players_data = item.get('value', [])
                    for player_props in players_data:
                        for prop in player_props:
                            if isinstance(prop, dict) and prop.get('name') == 'OwningPlayer' and prop.get('value') == 0:
                                # Found Colony 0, now find Resources
                                for res_prop in player_props:
                                    if isinstance(res_prop, dict) and res_prop.get('name') == 'Resources':
                                        resources_value = res_prop.get('value', 0)
                                        break
                                break
                    break
            
            backup_data.append({
                'timestamp': backup_dir.name,
                'resources': resources_value,
                'data': json_data
            })
            
        except Exception as e:
            print(f"❌ Error loading {backup_dir.name}: {e}")
    
    print(f"\n📊 Loaded {len(backup_data)} backup files")
    
    # Display Resources progression
    print("\n🔄 RESOURCES PROGRESSION:")
    print("-" * 40)
    for backup in backup_data:
        print(f"{backup['timestamp']:<25} Resources: {backup['resources']}")
    
    # Find the most interesting comparison (biggest Resources change)
    best_diff = None
    best_change = 0
    
    for i in range(len(backup_data) - 1):
        curr_resources = backup_data[i]['resources'] or 0
        next_resources = backup_data[i + 1]['resources'] or 0
        change = abs(next_resources - curr_resources)
        
        if change > best_change:
            best_change = change
            best_diff = (i, i + 1)
    
    if not best_diff:
        print("❌ No significant Resources changes found")
        return
    
    # Analyze the best difference
    idx1, idx2 = best_diff
    backup1 = backup_data[idx1]
    backup2 = backup_data[idx2]
    
    print(f"\n🎯 ANALYZING BIGGEST CHANGE:")
    print(f"   {backup1['timestamp']} → {backup2['timestamp']}")
    print(f"   Resources: {backup1['resources']} → {backup2['resources']} (Δ{backup2['resources'] - backup1['resources']:+d})")
    
    # Find differences between the two saves
    print(f"\n🔍 FINDING DIFFERENCES...")
    differences = deep_diff(backup1['data'], backup2['data'])
    
    # Filter for interesting differences (exclude known non-inputs)
    interesting_diffs = []
    for diff in differences:
        path = diff['path']
        
        # Skip known outputs and timestamps
        if any(skip in path for skip in ['PlayersSaveStates', 'timestamp', 'save_game_version']):
            continue
            
        # Focus on numeric changes that might be inputs
        if diff['type'] == 'value_change':
            old_val = diff['old_value']
            new_val = diff['new_value']
            
            # Look for numeric changes
            if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                change = new_val - old_val
                # Focus on changes that might correlate with Resources change
                if abs(change) > 0:
                    interesting_diffs.append({
                        'path': path,
                        'change': change,
                        'old_value': old_val,
                        'new_value': new_val
                    })
    
    # Sort by change magnitude
    interesting_diffs.sort(key=lambda x: abs(x['change']), reverse=True)
    
    print(f"\n📋 TOP CANDIDATES FOR RESOURCES INPUTS:")
    print("-" * 60)
    
    resources_change = backup2['resources'] - backup1['resources']
    
    for i, diff in enumerate(interesting_diffs[:20]):  # Show top 20
        correlation = ""
        if diff['change'] == resources_change:
            correlation = " ⭐ EXACT MATCH!"
        elif abs(diff['change']) == abs(resources_change):
            correlation = " 🔥 MAGNITUDE MATCH!"
        elif diff['change'] == -resources_change:
            correlation = " 🔄 INVERSE MATCH!"
        
        print(f"{i+1:2d}. {diff['path']}")
        print(f"    {diff['old_value']} → {diff['new_value']} (Δ{diff['change']:+.1f}){correlation}")
        print()
    
    # Look for array additions/removals that might be food items
    print(f"\n🍯 POTENTIAL FOOD/ITEM CHANGES:")
    print("-" * 40)
    
    for diff in differences:
        if diff['type'] in ['added', 'removed']:
            if any(keyword in diff['path'].lower() for keyword in ['food', 'item', 'resource', 'loot', 'ant']):
                print(f"{diff['type'].upper()}: {diff['path']}")
                if diff['type'] == 'added':
                    print(f"   Value: {diff['new_value']}")
                else:
                    print(f"   Value: {diff['old_value']}")
                print()
    
    print(f"\n💡 NEXT STEPS FOR REVERSE ENGINEERING:")
    print("=" * 50)
    print("1. Focus on the EXACT MATCH and MAGNITUDE MATCH candidates")
    print("2. Test modifying these values in a save file")
    print("3. Check if the Resources calculation changes accordingly")
    print("4. The real input is likely one of these top candidates")

if __name__ == "__main__":
    analyze_resource_inputs()
