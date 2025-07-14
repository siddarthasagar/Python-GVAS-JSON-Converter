#!/usr/bin/env python3
"""
Analyze the converted EotU JSON files to find game statistics
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_json_file(json_path):
    """Analyze a JSON file for game statistics"""
    print(f"\n📊 Analyzing {json_path.name}")
    print("="*50)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Count different property types
    property_counts = defaultdict(int)
    food_values = []
    resource_values = []
    max_food_values = []
    
    def count_properties(obj, path=""):
        """Recursively count properties in the JSON structure"""
        if isinstance(obj, dict):
            if 'type' in obj and 'name' in obj:
                prop_name = obj['name']
                property_counts[prop_name] += 1
                
                # Collect specific values
                if prop_name == "SavedCurrentFoodValue" and 'value' in obj:
                    food_values.append(obj['value'])
                elif prop_name == "SavedResourcesHeld" and 'value' in obj:
                    resource_values.append(obj['value'])
                elif prop_name == "SavedMaxFood" and 'value' in obj:
                    max_food_values.append(obj['value'])
            
            for key, value in obj.items():
                count_properties(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                count_properties(item, f"{path}[{i}]")
    
    count_properties(data)
    
    # Print key statistics
    print(f"SavedCurrentFoodValue instances: {property_counts['SavedCurrentFoodValue']}")
    print(f"SavedResourcesHeld instances: {property_counts['SavedResourcesHeld']}")
    print(f"SavedMaxFood instances: {property_counts['SavedMaxFood']}")
    
    if food_values:
        total_food = sum(food_values)
        non_zero_food = [v for v in food_values if v > 0]
        print(f"\nFood Analysis:")
        print(f"  Total food across all objects: {total_food}")
        print(f"  Non-zero food values: {len(non_zero_food)}")
        if non_zero_food:
            print(f"  Non-zero food values: {sorted(non_zero_food, reverse=True)[:10]}...")
    
    if resource_values:
        total_resources = sum(resource_values)
        non_zero_resources = [v for v in resource_values if v > 0]
        print(f"\nResource Analysis:")
        print(f"  Total resources: {total_resources}")
        print(f"  Non-zero resource values: {len(non_zero_resources)}")
        if non_zero_resources:
            print(f"  Non-zero resource values: {sorted(non_zero_resources, reverse=True)[:10]}...")
    
    if max_food_values:
        total_max_food = sum(max_food_values)
        non_zero_max = [v for v in max_food_values if v > 0]
        print(f"\nMax Food Analysis:")
        print(f"  Total max food capacity: {total_max_food}")
        print(f"  Non-zero max capacities: {len(non_zero_max)}")
        if non_zero_max:
            print(f"  Max capacity values: {sorted(set(non_zero_max), reverse=True)[:10]}...")
    
    # Look for specific game values from your analysis
    print(f"\n🎯 Looking for target values (67, 220, 457):")
    target_values = [67, 220, 457]
    for target in target_values:
        if target in food_values:
            print(f"  Found {target} in SavedCurrentFoodValue!")
        if target in resource_values:
            print(f"  Found {target} in SavedResourcesHeld!")
        if target in max_food_values:
            print(f"  Found {target} in SavedMaxFood!")
    
    return {
        'property_counts': dict(property_counts),
        'total_food': sum(food_values),
        'total_resources': sum(resource_values),
        'total_max_food': sum(max_food_values),
        'non_zero_food': len([v for v in food_values if v > 0]),
        'non_zero_resources': len([v for v in resource_values if v > 0])
    }

def main():
    """Main analysis function"""
    json_dir = Path("games_save_data/EotU/json")
    
    # Key files to analyze based on your research
    key_files = [
        "Colony1LevelData.json",  # Current game state (872 food instances)
        "Colony1.json",           # Colony metadata
        "Progress.json",          # Game progress
        "LevelSetup.json"         # Level configuration
    ]
    
    print("🔍 EotU Save File Analysis")
    print("Based on your save_file_analysis.md findings")
    
    for filename in key_files:
        json_path = json_dir / filename
        if json_path.exists():
            stats = analyze_json_file(json_path)
        else:
            print(f"❌ File not found: {filename}")
    
    print("\n" + "="*70)
    print("💡 Next Steps:")
    print("1. Look for patterns in non-zero values that sum to 67 (current food)")
    print("2. Search for values that sum to 220 (max food capacity)")  
    print("3. Find resource values that sum to 457 (royal jelly)")
    print("4. Use the JSON structure to modify specific values")
    print("5. Convert back to .sav format for testing")

if __name__ == "__main__":
    main()
