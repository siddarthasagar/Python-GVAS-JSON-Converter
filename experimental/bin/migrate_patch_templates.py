#!/usr/bin/env python3
"""
Migrate legacy patch templates to the new generic format for bin/apply_patch.py.
Retains legacy templates for fallback.
"""

import json
from pathlib import Path
import sys


def legacy_to_generic(legacy_patch):
    # If the loaded patch is a list, treat as already generic
    if isinstance(legacy_patch, list):
        return {"patches": legacy_patch}
    # Otherwise, handle dict format
    patches = []
    patch_data = legacy_patch.get("patches", {})
    if isinstance(patch_data, dict):
        for prop, value in patch_data.items():
            if value is not None:
                entry = {"type": "property", "path": [prop], "action": {"action": "set", "value": value}}
                patches.append(entry)
    elif isinstance(patch_data, list):
        patches = patch_data
    else:
        pass
    generic = {k: v for k, v in legacy_patch.items() if k != "patches"}
    generic["patches"] = patches
    return generic


def migrate_file(legacy_path, generic_path):
    with open(legacy_path, encoding="utf-8") as f:
        legacy_patch = json.load(f)
    # If file is a list, treat as already generic
    generic_patch = {"patches": legacy_patch} if isinstance(legacy_patch, list) else legacy_to_generic(legacy_patch)
    with open(generic_path, "w", encoding="utf-8") as f:
        json.dump(generic_patch, f, indent=2)
    print(f"Migrated {legacy_path} → {generic_path}")


def main():
    MIN_ARGS = 2  # script name + at least one legacy file
    if len(sys.argv) < MIN_ARGS:
        print("Usage: python migrate_patch_templates.py <legacy_patch_file1> [<legacy_patch_file2> ...]")
        sys.exit(1)
    for legacy_file in sys.argv[1:]:
        legacy_path = Path(legacy_file)
        generic_path = legacy_path.with_suffix(".generic.json")
        migrate_file(legacy_path, generic_path)


if __name__ == "__main__":
    main()
