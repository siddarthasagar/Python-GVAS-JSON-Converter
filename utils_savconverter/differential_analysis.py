#!/usr/bin/env python3
"""
Differential Analysis Tool for Resources Calculation
Find the actual inputs that drive Resources calculation by comparing save states
"""

import json
from pathlib import Path

from SavConverter import read_sav, sav_to_json


def deep_diff(obj1, obj2, path=""):
    """
    Deep comparison of two objects to find differences
    Returns a list of differences with their paths
    """
    differences = []

    # Early exit on type change
    if obj1.__class__ is not obj2.__class__:
        differences.append(
            {
                "path": path,
                "type": "type_change",
                "old_value": obj1,
                "new_value": obj2,
                "old_type": type(obj1).__name__,
                "new_type": type(obj2).__name__,
            }
        )
        return differences

    def diff_dict(d1, d2, base_path):
        # Check for added/removed keys
        keys1 = set(d1.keys())
        keys2 = set(d2.keys())

        for key in keys1 - keys2:
            differences.append(
                {
                    "path": f"{base_path}.{key}" if base_path else key,
                    "type": "removed",
                    "old_value": d1[key],
                    "new_value": None,
                }
            )

        for key in keys2 - keys1:
            differences.append(
                {
                    "path": f"{base_path}.{key}" if base_path else key,
                    "type": "added",
                    "old_value": None,
                    "new_value": d2[key],
                }
            )

        # Check for changed values
        for key in keys1 & keys2:
            new_path = f"{base_path}.{key}" if base_path else key
            differences.extend(deep_diff(d1[key], d2[key], new_path))

    def diff_list(l1, l2, base_path):
        # Compare list lengths first
        if len(l1) != len(l2):
            differences.append(
                {
                    "path": base_path,
                    "type": "length_change",
                    "old_value": f"length: {len(l1)}",
                    "new_value": f"length: {len(l2)}",
                }
            )

        # Compare elements
        min_len = min(len(l1), len(l2))
        for i in range(min_len):
            new_path = f"{base_path}[{i}]"
            differences.extend(deep_diff(l1[i], l2[i], new_path))

        # Handle extra elements
        if len(l1) > len(l2):
            for i in range(len(l2), len(l1)):
                differences.append(
                    {"path": f"{base_path}[{i}]", "type": "removed", "old_value": l1[i], "new_value": None}
                )
        elif len(l2) > len(l1):
            for i in range(len(l1), len(l2)):
                differences.append(
                    {"path": f"{base_path}[{i}]", "type": "added", "old_value": None, "new_value": l2[i]}
                )

    if isinstance(obj1, dict):
        diff_dict(obj1, obj2, path)
    elif isinstance(obj1, list):
        diff_list(obj1, obj2, path)
    elif obj1 != obj2:
        differences.append({"path": path, "type": "value_change", "old_value": obj1, "new_value": obj2})

    return differences


def _list_backup_dirs(backups_dir: Path):
    return sorted([d for d in backups_dir.iterdir() if d.is_dir() and d.name != "latest"])


def _extract_resources(json_data):
    for item in json_data:
        if item.get("name") != "PlayersSaveStates":
            continue
        for player_props in item.get("value", []):
            colony_zero = any(
                isinstance(prop, dict) and prop.get("name") == "OwningPlayer" and prop.get("value") == 0
                for prop in player_props
            )
            if not colony_zero:
                continue
            for res_prop in player_props:
                if isinstance(res_prop, dict) and res_prop.get("name") == "Resources":
                    return res_prop.get("value", 0)
            return None
    return None


def _load_backup_dir(backup_dir: Path):
    colony_file = backup_dir / "Colony1LevelData.sav"
    if not colony_file.exists():
        return None
    print(f"📄 Loading {backup_dir.name}...")
    properties = read_sav(str(colony_file))
    json_string = sav_to_json(properties, string=True)
    json_data = json.loads(json_string)
    return {
        "timestamp": backup_dir.name,
        "resources": _extract_resources(json_data),
        "data": json_data,
    }


def _find_best_diff(backup_data):
    MIN_COMPARE = 2
    if len(backup_data) < MIN_COMPARE:
        return None, 0

    def _res(idx: int) -> int:
        return backup_data[idx]["resources"] or 0

    pairs = [(i, i + 1) for i in range(len(backup_data) - 1)]
    if not pairs:
        return None, 0
    best_pair, best_change = max(
        ((p, abs(_res(p[1]) - _res(p[0]))) for p in pairs),
        key=lambda x: x[1],
    )
    return best_pair, best_change


def _filter_interesting_diffs(differences, skip_parts=("PlayersSaveStates", "timestamp", "save_game_version")):
    def allowed_path(path: str) -> bool:
        return not any(p in path for p in skip_parts)

    def is_numeric_change(d):
        if d.get("type") != "value_change":
            return False
        old_val = d.get("old_value")
        new_val = d.get("new_value")
        return isinstance(old_val, (int | float)) and isinstance(new_val, (int | float)) and (old_val != new_val)

    return [
        {
            "path": d["path"],
            "change": d["new_value"] - d["old_value"],
            "old_value": d["old_value"],
            "new_value": d["new_value"],
        }
        for d in differences
        if allowed_path(d["path"]) and is_numeric_change(d)
    ]


def _print_top_candidates(diffs, backup1, backup2):
    print("\n📋 TOP CANDIDATES FOR RESOURCES INPUTS:")
    print("-" * 60)
    resources_change = (backup2["resources"] or 0) - (backup1["resources"] or 0)
    for i, diff in enumerate(diffs[:20]):
        correlation = ""
        if diff["change"] == resources_change:
            correlation = " ⭐ EXACT MATCH!"
        elif abs(diff["change"]) == abs(resources_change):
            correlation = " 🔥 MAGNITUDE MATCH!"
        elif diff["change"] == -resources_change:
            correlation = " 🔄 INVERSE MATCH!"
        print(f"{i + 1:2d}. {diff['path']}")
        print(f"    {diff['old_value']} → {diff['new_value']} (Δ{diff['change']:+.1f}){correlation}")
        print()


def _print_item_changes(differences):
    print("\n🍯 POTENTIAL FOOD/ITEM CHANGES:")
    print("-" * 40)
    keywords = ("food", "item", "resource", "loot", "ant")
    for d in differences:
        if d.get("type") in ("added", "removed") and any(k in d.get("path", "").lower() for k in keywords):
            print(f"{d['type'].upper()}: {d['path']}")
            print(f"   Value: {d['new_value'] if d['type'] == 'added' else d['old_value']}")
            print()


def analyze_resource_inputs():
    """
    Analyze backup files to find what inputs drive Resources calculation
    (refactored to reduce branching/statements for Ruff PLR0912/PLR0915)
    """
    print("🔍 DIFFERENTIAL ANALYSIS: Finding Resources Calculation Inputs")
    print("=" * 80)

    backups_dir = Path("backups/EotU/SaveGames")
    backup_dirs = _list_backup_dirs(backups_dir)

    MIN_BACKUPS = 2
    if len(backup_dirs) < MIN_BACKUPS:
        print(f"❌ Need at least {MIN_BACKUPS} backup files for differential analysis")
        return

    backup_data = []
    for backup_dir in backup_dirs[:5]:
        try:
            loaded = _load_backup_dir(backup_dir)
            if loaded is not None:
                backup_data.append(loaded)
        except Exception as e:
            print(f"❌ Error loading {backup_dir.name}: {e}")

    print(f"\n📊 Loaded {len(backup_data)} backup files")

    print("\n🔄 RESOURCES PROGRESSION:")
    print("-" * 40)
    for backup in backup_data:
        print(f"{backup['timestamp']:<25} Resources: {backup['resources']}")

    best_diff, best_change = _find_best_diff(backup_data)
    if not best_diff or best_change == 0:
        print("❌ No significant Resources changes found")
        return

    idx1, idx2 = best_diff
    backup1 = backup_data[idx1]
    backup2 = backup_data[idx2]

    print("\n🎯 ANALYZING BIGGEST CHANGE:")
    print(f"   {backup1['timestamp']} → {backup2['timestamp']}")
    delta = (backup2["resources"] or 0) - (backup1["resources"] or 0)
    print(f"   Resources: {backup1['resources']} → {backup2['resources']} (Δ{delta:+d})")

    print("\n🔍 FINDING DIFFERENCES...")
    differences = deep_diff(backup1["data"], backup2["data"])

    interesting_diffs = _filter_interesting_diffs(differences)
    interesting_diffs.sort(key=lambda x: abs(x["change"]), reverse=True)

    _print_top_candidates(interesting_diffs, backup1, backup2)
    _print_item_changes(differences)


if __name__ == "__main__":
    analyze_resource_inputs()
