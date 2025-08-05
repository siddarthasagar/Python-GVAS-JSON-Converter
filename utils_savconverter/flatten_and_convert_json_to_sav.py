import json
import sys

from SavConverter.JsonToSav import json_to_sav


def extract_all_values(properties):
    result = []
    for key, section in properties.items():
        try:
            value = section["Array"]["Struct"]["value"]
            if isinstance(value, list):
                # For each item, extract the inner dict from "Struct" and add "type", "subtype", "value", and "name"
                for item in value:
                    if "Struct" in item:
                        struct = item["Struct"]
                        struct["type"] = "StructProperty"
                        if "subtype" not in struct or struct["subtype"] is None:
                            struct["subtype"] = ""
                        if "value" not in struct:
                            struct["value"] = []
                        if "name" not in struct:
                            struct["name"] = key
                        result.append(struct)
        except Exception:
            continue
    return result


MIN_ARGS = 3
if len(sys.argv) != MIN_ARGS:
    print("Usage: python3 flatten_and_convert_json_to_sav.py input.json output.sav")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]


with open(input_file, encoding="utf-8") as fin:
    data = json.load(fin)

properties = data["root"]["properties"]
flat_list = extract_all_values(properties)

# json_to_sav returns bytes
sav_bytes = json_to_sav(flat_list)

# Open output in binary mode and write bytes to satisfy typing (BinaryIO)
with open(output_file, "wb") as bout:
    bout.write(sav_bytes)

print(f"Converted {input_file} to {output_file} using {len(flat_list)} save objects.")
