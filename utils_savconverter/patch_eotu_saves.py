#!/usr/bin/env python3
"""
Enhanced EotU Save File Patcher
Patches Empires of the Undergrowth save files with improved targeting and validation
"""

import json
import sys
import os
from pathlib import Path
from SavConverter import load_json, json_to_sav

class EotUPatcher:
    def __init__(self, json_file_path, patch_file_path):
        self.json_file_path = Path(json_file_path)
        self.patch_file_path = Path(patch_file_path)
        self.data = None
        self.patches = None
        self.applied_patches = []
        
    def load_data(self):
        """Load JSON save data"""
        print(f"Loading save data from: {self.json_file_path}")
        self.data = load_json(str(self.json_file_path))
        print(f"✅ Loaded {len(self.data)} data items")
        
    def load_patches(self):
        """Load patch configuration"""
        print(f"Loading patches from: {self.patch_file_path}")
        with open(self.patch_file_path, 'r') as f:
            patch_config = json.load(f)
        
        self.patches = patch_config.get('patches', {})
        print(f"✅ Loaded {len(self.patches)} patch definitions")
        
    def find_players_save_states(self):
        """Find PlayersSaveStates section in the data"""
        for i, item in enumerate(self.data):
            if isinstance(item, dict) and item.get('name') == 'PlayersSaveStates':
                return item['value']
        return None
    
    def apply_patches(self):
        """Apply patches to the save data"""
        players_states = self.find_players_save_states()
        
        if not players_states:
            print("❌ PlayersSaveStates not found!")
            return False
        
        print(f"Found {len(players_states)} players")
        
        # Target Player 1 (Colony 0) - this is where the UI values are stored
        target_player = None
        for player in players_states:
            if isinstance(player, list):
                for prop in player:
                    if isinstance(prop, dict) and prop.get('name') == 'OwningPlayer' and prop.get('value') == 0:
                        target_player = player
                        break
                if target_player:
                    break
        
        if not target_player:
            print("❌ Target player (Colony 0) not found!")
            return False
        
        print("✅ Found target player (Colony 0)")
        
        # Apply each patch
        for patch_name, patch_value in self.patches.items():
            if patch_value is not None:  # Skip null patches
                success = self._apply_single_patch(target_player, patch_name, patch_value)
                if success:
                    self.applied_patches.append(f"{patch_name}: {patch_value}")
        
        return len(self.applied_patches) > 0
    
    def _apply_single_patch(self, player_data, property_name, new_value):
        """Apply a single patch to player data"""
        for prop in player_data:
            if isinstance(prop, dict) and prop.get('name') == property_name:
                old_value = prop.get('value', 'N/A')
                prop['value'] = new_value
                print(f"✅ Patched {property_name}: {old_value} → {new_value}")
                return True
        
        print(f"❌ Property '{property_name}' not found")
        return False
    
    def save_patched_data(self, output_path):
        """Convert patched JSON back to .sav format"""
        print(f"Converting patched data to: {output_path}")
        
        try:
            binary_data = json_to_sav(self.data)
            with open(output_path, 'wb') as f:
                f.write(binary_data)
            print(f"✅ Patched save file created: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving patched file: {e}")
            return False
    
    def run(self, output_path):
        """Run the complete patching process"""
        print("🚀 Starting EotU Save File Patcher")
        print("=" * 50)
        
        try:
            # Load data and patches
            self.load_data()
            self.load_patches()
            
            # Apply patches
            if self.apply_patches():
                print(f"\n✅ Applied {len(self.applied_patches)} patches:")
                for patch in self.applied_patches:
                    print(f"  - {patch}")
                
                # Save patched data
                if self.save_patched_data(output_path):
                    print(f"\n🎉 SUCCESS! Patched save file ready at: {output_path}")
                    return True
            else:
                print("\n❌ No patches were applied")
                return False
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            return False

def main():
    """Main entry point"""
    if len(sys.argv) != 4:
        print("Usage: python patch_eotu_saves.py <json_file> <patch_file> <output_sav>")
        print("Example: python patch_eotu_saves.py games_save_data/EotU/json/Colony1LevelData.json patches/patch_template.json Colony1LevelData_patched.sav")
        sys.exit(1)
    
    json_file = sys.argv[1]
    patch_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Validate input files exist
    if not Path(json_file).exists():
        print(f"❌ JSON file not found: {json_file}")
        sys.exit(1)
    
    if not Path(patch_file).exists():
        print(f"❌ Patch file not found: {patch_file}")
        sys.exit(1)
    
    # Run patcher
    patcher = EotUPatcher(json_file, patch_file)
    success = patcher.run(output_file)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
