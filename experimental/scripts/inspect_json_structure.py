#!/usr/bin/env python3

import json


def print_keys(obj, path="", depth=0, max_depth=3):
    if depth > max_depth:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            print(f"{'  ' * depth}{path}.{k} ({type(v).__name__})")
            print_keys(v, f"{path}.{k}", depth + 1, max_depth)
    elif isinstance(obj, list):
        print(f"{'  ' * depth}{path} [list of {len(obj)}]")
        if obj and depth < max_depth:
            print_keys(obj[0], f"{path}[0]", depth + 1, max_depth)


def main():
    for fname in ["test_backup.json", "test_backup2.json"]:
        print(f"\n=== {fname} ===")
        with open(fname) as f:
            data = json.load(f)
        print_keys(data, path="root", depth=0, max_depth=2)


if __name__ == "__main__":
    main()
