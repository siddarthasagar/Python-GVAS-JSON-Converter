#!/usr/bin/env python3
"""
EotU Save File Patcher
=====================

A tool to safely modify Empires of the Undergrowth save files by:
1. Converting .sav files to JSON
2. Applying patches to specific game values
3. Converting back to .sav format
4. Creating backups and safety checks

Based on the analysis that found values at:
- Resources (Food): line 1126907
- RoyalJelly: line 1126917
- Territory: line 1126912
- Score: line 1126922
- TotalResourcesGathered: line 1126927
- TilesExcavated: line 1126932
"""

from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any

# Import the SavConverter library
from SavConverter import json_to_sav, load_json


class EotUPatcher:
    """EotU Save File Patcher with safety features"""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.json_path = self.base_path / "games_save_data/EotU/json"
        self.saves_path = self.base_path / "games_save_data/EotU/SaveGames"
        self.backup_path = self.base_path / "backups/EotU/SaveGames"
        self.patches_path = self.base_path / "patches"

        # Ensure directories exist
        self.patches_path.mkdir(parents=True, exist_ok=True)

    def create_patch_backup(self) -> str:
        """Create a backup before applying patches"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_path / f"pre_patch_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        if self.saves_path.exists():
            for file in self.saves_path.glob("*.sav"):
                shutil.copy2(file, backup_dir)

        print(f"✅ Pre-patch backup created: {backup_dir}")
        return str(backup_dir)

    def apply_patches(self, patches: dict[str, Any], target_file: str = "Colony1LevelData") -> bool:
        """Apply patches to a specific save file"""
        try:
            # Load the JSON file
            json_file = self.json_path / f"{target_file}.json"
            if not json_file.exists():
                print(f"❌ JSON file not found: {json_file}")
                return False

            print(f"📄 Loading {json_file}")
            data = load_json(str(json_file))

            # Apply patches
            modifications_made = 0
            for property_name, new_value in patches.items():
                if self._patch_property(data, property_name, new_value):
                    modifications_made += 1
                    print(f"✅ Patched {property_name}: {new_value}")
                else:
                    print(f"⚠️  Could not find property: {property_name}")

            if modifications_made == 0:
                print("❌ No modifications made")
                return False

            # Convert back to .sav
            print("🔧 Converting back to .sav format...")
            binary_data = json_to_sav(data)

            # Write the modified save file
            output_file = self.saves_path / f"{target_file}.sav"
            with open(output_file, "wb") as f:
                f.write(binary_data)

            print(f"✅ Patched save file created: {output_file}")
            print(f"📊 Applied {modifications_made} patches")
            return True

        except Exception as e:
            print(f"❌ Error applying patches: {str(e)}")
            return False

    def _patch_property(self, data: dict, property_name: str, new_value: Any) -> bool:
        """Recursively search and patch a property in the JSON structure"""
        return self._search_and_patch(data, property_name, new_value)

    def _search_and_patch(self, obj: Any, target_name: str, new_value: Any) -> bool:
        """Recursively search for a property and patch it - targets the LAST non-zero occurrence"""
        found_objects: list[dict] = []
        self._collect_property_objects(obj, target_name, found_objects)

        if not found_objects:
            return False

        # Find the best target (last non-zero value, or last value if all zero)
        non_zero_objects = [o for o in found_objects if o.get("value", 0) != 0]
        target_obj = non_zero_objects[-1] if non_zero_objects else found_objects[-1]

        # Apply the patch
        old_value = target_obj["value"]
        target_obj["value"] = new_value
        print(f"  🔄 {target_name}: {old_value} → {new_value}")
        return True

    def _collect_property_objects(self, obj: Any, target_name: str, found_objects: list[dict]) -> None:
        """Collect all instances of a property object"""
        if isinstance(obj, dict):
            if "name" in obj and obj.get("name") == target_name and "value" in obj:
                found_objects.append(obj)

            for value in obj.values():
                self._collect_property_objects(value, target_name, found_objects)

        elif isinstance(obj, list):
            for item in obj:
                self._collect_property_objects(item, target_name, found_objects)

    def get_current_values(self, target_file: str = "Colony1LevelData") -> dict[str, Any]:
        """Get current values of key properties"""
        json_file = self.json_path / f"{target_file}.json"
        if not json_file.exists():
            return {}

        data = load_json(str(json_file))
        values = {}

        # Properties we're interested in
        properties = ["Resources", "RoyalJelly", "Territory", "Score", "TotalResourcesGathered", "TilesExcavated"]

        for prop in properties:
            value = self._find_property_value(data, prop)
            if value is not None:
                values[prop] = value

        return values

    def _find_property_value(self, obj: Any, target_name: str) -> Any | None:
        """Recursively find a property value - returns the LAST non-zero occurrence"""
        found_values: list[Any] = []
        self._collect_property_values(obj, target_name, found_values)

        # Return the last non-zero value, or the last value if all are zero
        non_zero_values = [v for v in found_values if v != 0]
        if non_zero_values:
            return non_zero_values[-1]  # Last non-zero value
        elif found_values:
            return found_values[-1]  # Last value (even if zero)
        else:
            return None

    def _collect_property_values(self, obj: Any, target_name: str, found_values: list[Any]) -> None:
        """Collect all instances of a property value"""
        if isinstance(obj, dict):
            if "name" in obj and obj.get("name") == target_name and "value" in obj:
                found_values.append(obj["value"])

            for value in obj.values():
                self._collect_property_values(value, target_name, found_values)

        elif isinstance(obj, list):
            for item in obj:
                self._collect_property_values(item, target_name, found_values)

    def create_patch_template(self) -> str:
        """Create a patch template file"""
        current_values = self.get_current_values()

        template = {
            "_description": "EotU Save File Patch Template",
            "_instructions": [
                "Modify the values below to patch your save file",
                "Set any value to null to skip patching that property",
                "Use 'make patch' to apply this patch file",
            ],
            "_current_values": current_values,
            "patches": {
                "Resources": None,  # Current food storage
                "RoyalJelly": None,  # Royal jelly count
                "Territory": None,  # Territory control
                "Score": None,  # Player score
                "TotalResourcesGathered": None,  # Total resources collected
                "TilesExcavated": None,  # Tiles dug
            },
        }

        patch_file = self.patches_path / "patch_template.json"
        with open(patch_file, "w") as f:
            json.dump(template, f, indent=2)

        print(f"✅ Patch template created: {patch_file}")
        print(f"📝 Edit the template and run: python patch_saves.py apply {patch_file}")
        return str(patch_file)


def _print_usage():
    print("🎮 EotU Save File Patcher")
    print("=" * 30)
    print("Usage:")
    print("  python patch_saves.py template    - Create patch template")
    print("  python patch_saves.py current     - Show current values")
    print("  python patch_saves.py apply <file>- Apply patch file")
    print("  python patch_saves.py quick       - Quick patch (interactive)")
    print("")
    print("Examples:")
    print("  python patch_saves.py template")
    print("  python patch_saves.py apply patches/my_patch.json")


def _dispatch_command(patcher: EotUPatcher, argv: list[str]) -> None:
    command = argv[1].lower()

    def handle_current():
        print("📊 Current Save File Values")
        print("=" * 30)
        values = patcher.get_current_values()
        for prop, value in values.items():
            print(f"  {prop}: {value}")

    def handle_apply():
        MIN_ARGS_APPLY = 3
        if len(argv) < MIN_ARGS_APPLY:
            print("❌ Please specify patch file")
            return
        patch_file = argv[2]
        if not os.path.exists(patch_file):
            print(f"❌ Patch file not found: {patch_file}")
            return
        with open(patch_file) as f:
            patch_data = json.load(f)
        patches = {k: v for k, v in patch_data.get("patches", {}).items() if v is not None}
        if not patches:
            print("❌ No patches to apply (all values are null)")
            return
        print(f"🔧 Applying patches from: {patch_file}")
        backup_dir = patcher.create_patch_backup()
        if patcher.apply_patches(patches):
            print("🎉 Patches applied successfully!")
            print(f"💾 Backup saved to: {backup_dir}")
        else:
            print("❌ Failed to apply patches")

    def handle_quick():
        print("🚀 Quick Patch Mode")
        print("=" * 20)
        current_values = patcher.get_current_values()
        patches: dict[str, Any] = {}
        for prop, current in current_values.items():
            new_value = input(f"{prop} (current: {current}): ").strip()
            if new_value and new_value.isdigit():
                patches[prop] = int(new_value)
        if not patches:
            print("❌ No patches to apply")
            return
        backup_dir = patcher.create_patch_backup()
        if patcher.apply_patches(patches):
            print("🎉 Quick patches applied!")
            print(f"💾 Backup saved to: {backup_dir}")

    handlers = {
        "template": lambda: patcher.create_patch_template(),
        "current": handle_current,
        "apply": handle_apply,
        "quick": handle_quick,
    }

    if command in handlers:
        handlers[command]()
    else:
        print(f"❌ Unknown command: {command}")


def main():
    """Main patcher interface"""
    patcher = EotUPatcher()

    MIN_ARGS_BASE = 2
    if len(sys.argv) < MIN_ARGS_BASE:
        _print_usage()
        return

    _dispatch_command(patcher, sys.argv)


if __name__ == "__main__":
    main()
