#!/usr/bin/env python3

import json

# Load the test_backup2.json file
with open('test_backup2.json', 'r') as f:
    data = json.load(f)

# Navigate to PlayersSaveStates_0 and look for Resources
players_save_states = data.get('PlayersSaveStates_0', {}).get('Array', {}).get('Struct', {}).get('value', [])

print("=== test_backup2.json Resources Analysis ===")
print(f"Number of player entries: {len(players_save_states)}")

# Extract Resources values for each player
for i, player in enumerate(players_save_states):
    player_struct = player.get('Struct', {})
    
    # Look for Resources_0 key
    resources_0 = player_struct.get('Resources_0', {})
    if resources_0:
        resources_value = resources_0.get('Int', 'Not found')
        print(f"Player {i} Resources_0: {resources_value}")
    else:
        print(f"Player {i}: Resources_0 not found")
