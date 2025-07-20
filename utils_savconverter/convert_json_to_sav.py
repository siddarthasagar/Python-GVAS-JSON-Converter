import sys
import json
from SavConverter.JsonToSav import json_to_sav

if len(sys.argv) != 3:
    print("Usage: python3 convert_json_to_sav.py input.json output.sav")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "r") as f:
    data = json.load(f)

sav_bytes = json_to_sav(data)

with open(output_file, "wb") as f:
    f.write(sav_bytes)

print(f"Converted {input_file} to {output_file}")
