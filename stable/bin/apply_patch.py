#!/usr/bin/env python3
import argparse
import json
import logging
import sys
from typing import Any


def setup_logger():
    logger = logging.getLogger("apply_patch")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def parse_args():
    parser = argparse.ArgumentParser(description="Generic patching script for save files.")
    parser.add_argument("input_save", help="Path to input save file (JSON)")
    parser.add_argument("patch_template", help="Path to patch template (JSON)")
    parser.add_argument("output_file", help="Path to output file (JSON)")
    return parser.parse_args()


def load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_by_path(obj: Any, path: list[str]):
    """Traverse obj by path, return reference to value."""
    for key in path[:-1]:
        obj = obj[key]
    return obj, path[-1]


def apply_action(target: Any, key: str, action: dict[str, Any], logger: logging.Logger):
    act_type = action.get("action")
    value = action.get("value")
    if act_type == "set":
        old = target.get(key)
        target[key] = value
        logger.info(f"Set {key}: {old} -> {value}")
    elif act_type == "increment":
        old = target.get(key, 0)
        target[key] = old + value
        logger.info(f"Increment {key}: {old} + {value} -> {target[key]}")
    else:
        logger.warning(f"Unknown action type: {act_type} for key: {key}")


def apply_patch(save_data: dict[str, Any], patch_template: list[dict[str, Any]], logger: logging.Logger):
    for entry in patch_template:
        patch_type = entry.get("type")
        path = entry.get("path")
        action = entry.get("action")
        # Skip if new_value is null (None)
        if entry.get("new_value", "not_present") is None:
            logger.info(f"Skipping patch entry with null new_value: {entry}")
            continue
        if not (patch_type and path and action):
            logger.warning(f"Skipping incomplete patch entry: {entry}")
            continue
        # For future extensibility, patch_type can be used for custom logic
        try:
            target, key = get_by_path(save_data, path)
            apply_action(target, key, action, logger)
        except Exception as e:
            logger.error(f"Failed to apply patch {entry}: {e}")


def main():
    args = parse_args()
    logger = setup_logger()
    save_data = load_json(args.input_save)
    patch_template = load_json(args.patch_template)
    apply_patch(save_data, patch_template, logger)
    save_json(args.output_file, save_data)
    logger.info(f"Patching complete. Output saved to {args.output_file}")


if __name__ == "__main__":
    main()
