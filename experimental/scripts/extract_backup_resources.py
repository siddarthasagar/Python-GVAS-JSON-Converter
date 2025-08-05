#!/usr/bin/env python3

import re

print("🎯 EXTRACTING RESOURCES FROM BACKUP FILES")
print("=" * 50)


def extract_resources_from_backup(filename):
    """Extract all Resources_0 values from a backup file"""
    print(f"\n📁 Analyzing {filename}:")

    with open(filename) as f:
        content = f.read()

    # Use regex to find all Resources_0 values
    # Pattern needs to handle nested structure with tag/data/Other/IntProperty
    pattern = r'"Resources_0":\s*{[^}]*?"tag":[^}]*?"data":[^}]*?"Other":[^}]*?"IntProperty"[^}]*?},\s*"Int":\s*(\d+)'
    matches = re.findall(pattern, content, re.DOTALL)

    # Convert to integers and get unique values
    resource_values = [int(match) for match in matches]
    unique_values = sorted(set(resource_values))

    print(f"   Total Resources_0 entries: {len(resource_values)}")
    print(f"   Unique values: {unique_values}")

    # Count occurrences of each value
    value_counts = {}
    for value in resource_values:
        value_counts[value] = value_counts.get(value, 0) + 1

    print("   Value distribution:")
    for value, count in sorted(value_counts.items()):
        print(f"     {value}: {count} times")

    return resource_values, unique_values


# Analyze both backup files
backup1_values, backup1_unique = extract_resources_from_backup("test_backup.json")
backup2_values, backup2_unique = extract_resources_from_backup("test_backup2.json")

print("\n" + "=" * 50)
print("🔍 COMPARISON ANALYSIS:")

print(f"\nBackup 1 unique values: {backup1_unique}")
print(f"Backup 2 unique values: {backup2_unique}")

# Find differences
only_in_backup1 = set(backup1_unique) - set(backup2_unique)
only_in_backup2 = set(backup2_unique) - set(backup1_unique)
common_values = set(backup1_unique) & set(backup2_unique)

if only_in_backup1:
    print(f"\nValues only in Backup 1: {sorted(only_in_backup1)}")
if only_in_backup2:
    print(f"Values only in Backup 2: {sorted(only_in_backup2)}")
print(f"Common values: {sorted(common_values)}")

print("\n🎯 PLAYER RESOURCES PROGRESSION:")
print("Looking for the main player Resources values...")

# The highest values are likely the main player resources
if backup1_unique:
    max_backup1 = max(backup1_unique)
    print(f"Backup 1 max Resources: {max_backup1}")

if backup2_unique:
    max_backup2 = max(backup2_unique)
    print(f"Backup 2 max Resources: {max_backup2}")

    if backup1_unique:
        change = max_backup2 - max_backup1
        print(f"Change: {change:+d}")
