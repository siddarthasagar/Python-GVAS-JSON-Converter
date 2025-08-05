#!/usr/bin/env python3
"""
Convert Empires of the Undergrowth save files to JSON format
"""

from pathlib import Path

# Import the SavConverter library
from SavConverter import read_sav, sav_to_json


def convert_sav_to_json(sav_path, json_path):
    """Convert a single .sav file to JSON format"""
    try:
        print(f"Converting {sav_path.name}...")

        # Read the .sav file
        properties = read_sav(str(sav_path))

        # Convert to JSON
        json_output = sav_to_json(properties, string=True)

        # Write JSON to file
        with open(json_path, "w", encoding="utf-8") as json_file:
            json_file.write(json_output)

        print(f"✅ Successfully converted to {json_path.name}")
        return True

    except Exception as e:
        print(f"❌ Error converting {sav_path.name}: {str(e)}")
        return False


def main():
    """Main conversion function"""
    # Define paths
    save_games_dir = Path("games_save_data/EotU/SaveGames")
    json_output_dir = Path("games_save_data/EotU/json")

    # Check if directories exist
    if not save_games_dir.exists():
        print(f"❌ SaveGames directory not found: {save_games_dir}")
        return

    # Create JSON output directory if it doesn't exist
    json_output_dir.mkdir(parents=True, exist_ok=True)

    # Find all .sav files
    sav_files = list(save_games_dir.glob("*.sav"))

    if not sav_files:
        print("❌ No .sav files found in SaveGames directory")
        return

    print(f"Found {len(sav_files)} .sav files to convert...")
    print("=" * 50)

    # Convert each .sav file
    successful_conversions = 0
    failed_conversions = 0

    for sav_file in sorted(sav_files):
        # Skip steam_autocloud.vdf as it's not a GVAS file
        if sav_file.name == "steam_autocloud.vdf":
            print(f"⏭️ Skipping {sav_file.name} (not a GVAS file)")
            continue

        # Create corresponding JSON filename
        json_filename = sav_file.stem + ".json"
        json_path = json_output_dir / json_filename

        # Convert the file
        if convert_sav_to_json(sav_file, json_path):
            successful_conversions += 1
        else:
            failed_conversions += 1

    # Summary
    print("=" * 50)
    print("Conversion complete!")
    print(f"✅ Successful: {successful_conversions}")
    print(f"❌ Failed: {failed_conversions}")
    print(f"📁 JSON files saved to: {json_output_dir}")


if __name__ == "__main__":
    main()
