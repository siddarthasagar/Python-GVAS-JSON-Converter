# Flexible Patching System Design

This document outlines the design for a new, flexible patching system for Empires of the Undergrowth save files.

## 1. Limitations of the Current System

The existing patching workflow is hardcoded for a single purpose: modifying food values.

- **`create_patch_template.py`**: Only extracts `SavedFoodHeld` from `ResourceBaseSaveStates`.
- **`uesave_food_patcher.py`**: Can only patch the `SavedFoodHeld` value in a predetermined JSON structure.
- **`Makefile`**: The entire pipeline is explicitly for "food" patches.

This makes it impossible to patch other parts of the save file, such as "jerry" or "territory" data, without creating entirely new scripts and Makefile logic for each type.

## 2. Proposed Generic Patch Template

To address these limitations, we will introduce a new generic JSON patch template format. This format is self-describing, allowing a single, intelligent patcher script to handle various patch types.

### 2.1. Structure Overview

The template consists of a `metadata` block and a list of `patch_operations`.

```json
{
  "metadata": {
    "version": "1.0",
    "patch_type": "food",
    "description": "A brief description of what this patch does.",
    "source_file": "The original save file this was based on."
  },
  "patch_operations": [
    // One or more patch operations go here
  ]
}
```

### 2.2. `patch_operations`

Each object in the `patch_operations` array defines a set of changes to be applied to a specific part of the save file's JSON structure.

- **`target`**: Specifies the array of objects to be modified.
  - `type`: The type of target (e.g., `array_property`).
  - `path`: A dot-notation path to the target array (e.g., `root.properties.SomeArray.Array.Struct.value`).
- **`actions`**: A list of modifications to apply to the `target` array.
  - `type`: The type of action (e.g., `update_by_index`).
  - `index`: The index of the element to modify in the target array.
  - `enabled`: A boolean flag to easily enable or disable a specific change.
  - `payload`: An object defining the change.
    - `path`: A relative dot-notation path *within* the array element to the property to be changed.
    - `value`: The new value to assign.
  - `description`: A human-readable note about the change.

### 2.3. Example: `food-patch.json`

```json
{
  "metadata": {
    "version": "1.0",
    "patch_type": "food",
    "description": "Patches food values in ResourceBaseSaveStates.",
    "source_file": "Colony1Stage2.sav"
  },
  "patch_operations": [
    {
      "target": {
        "type": "array_property",
        "path": "root.properties.ResourceBaseSaveStates_0.Array.Struct.value"
      },
      "actions": [
        {
          "type": "update_by_index",
          "index": 0,
          "enabled": true,
          "payload": {
            "path": "Struct.SavedFoodHeld_0.Int",
            "value": 9999
          },
          "description": "Node 0"
        }
      ]
    }
  ]
}
```

### 2.4. Example: `territory-patch.json`

This demonstrates how the same structure can be used for a completely different patch type.

```json
{
  "metadata": {
    "version": "1.0",
    "patch_type": "territory",
    "description": "Expands territory control points.",
    "source_file": "Colony1LevelData.sav"
  },
  "patch_operations": [
    {
      "target": {
        "type": "array_property",
        "path": "root.properties.TerritoryControlPoints.Array.Struct.value"
      },
      "actions": [
        {
          "type": "update_by_index",
          "index": 0,
          "enabled": true,
          "payload": {
            "path": "Struct.OwningPlayer.Int",
            "value": 1
          },
          "description": "Capture control point 0 for Player 1"
        }
      ]
    }
  ]
}
```

## 3. Next Steps

The subsequent steps in this project will be:
1.  **Design `bin/apply_patch.py`**: A new Python script that can parse and apply these generic patch templates.
2.  **Update `Makefile`**: Modify the Makefile to use the new script and manage different `PATCH_TYPE`s.
3.  **Create `docs/patching_workflow.md`**: Document the end-to-end user workflow for creating and applying these new patches.
## 4. Design of `bin/apply_patch.py`

This script will be the core of the new patching system. It will be responsible for reading the generic patch template and applying it to the target JSON file.

### 4.1. Core Logic

The script will perform the following steps:

1.  **Load Inputs**: Load the target JSON save file and the patch template.
2.  **Validate Metadata**: Check the `patch_type` and `version` from the template's metadata to ensure compatibility.
3.  **Iterate Operations**: Loop through each object in the `patch_operations` array.
4.  **Locate Target**: For each operation, use the `target.path` to navigate the JSON data and find the array to be modified.
5.  **Apply Actions**: Loop through the `actions` array and apply each one to the target array.
    - If `enabled` is `false`, skip the action.
    - Use the `index` to select the correct element.
    - Use the `payload.path` to find the property to change within the element.
    - Set the property to the `payload.value`.
6.  **Save Output**: Write the modified JSON data to the specified output file.

### 4.2. Key Functions (Pseudocode)

```python
def load_json(path):
    # ... loads a JSON file ...

def save_json(path, data):
    # ... saves a JSON file ...

def get_nested_value(data, path_str):
    # Navigates a dictionary using a dot-notation path string
    # e.g., "root.properties.SomeArray.Array.Struct.value"
    # Returns the value at that path.

def set_nested_value(data, path_str, value):
    # Navigates a dictionary and sets a value at the given path.

def apply_patch(input_json_path, output_json_path, patch_template_path):
    # 1. Load all three files
    save_data = load_json(input_json_path)
    patch_data = load_json(patch_template_path)

    # 2. (Optional) Validate metadata
    print(f"Applying patch: {patch_data['metadata']['description']}")

    # 3. Iterate through operations
    for op in patch_data["patch_operations"]:
        # 4. Locate the target array
        target_array = get_nested_value(save_data, op["target"]["path"])

        # 5. Apply actions to the array
        for action in op["actions"]:
            if action["enabled"]:
                element = target_array[action["index"]]
                set_nested_value(element, action["payload"]["path"], action["payload"]["value"])

    # 6. Save the modified data
    save_json(output_json_path, save_data)
```

This design ensures the patcher is completely agnostic to the *type* of data being changed. It only needs to know how to follow the paths provided in the template.
## 5. `Makefile` Integration

To integrate the new script and manage different patch types, the `Makefile` will be updated with the following changes:

### 5.1. New `PATCH_TYPE` Variable

A new variable will be introduced to allow users to specify the type of patch they are working with.

```makefile
# Default patch type
PATCH_TYPE ?= food

# The patch template file will be derived from the patch type
PATCH_TEMPLATE := $(PATCH_DIR)/$(PATCH_TYPE)_patch.json
```

This will allow users to run `make patch-apply PATCH_TYPE=territory` to use `patches/territory_patch.json`.

### 5.2. Updated Patching Targets

The existing patch targets (`patch-uesave`, `patch-validate`, etc.) will be modified to use the new generic `apply_patch.py` script.

**Old Target:**
```makefile
patch-uesave: extract-uesave
	@python3 bin/uesave_food_patcher.py ...
```

**New Target:**
```makefile
patch-apply-generic: extract-uesave
	@python3 bin/apply_patch.py \
		"$(TEMP_DIR)/$${save}_working.json" \
		"$(TEMP_DIR)/$${save}_patched.json" \
		"$(PATCH_TEMPLATE)"
```

The `patch-create` target will also need to be updated to call a new, generic template creation script (or be adapted to take a `PATCH_TYPE` argument).

### 5.3. Example Workflow

The new workflow in the `Makefile` would look like this:

1.  **`make patch-create PATCH_TYPE=food`**: A (yet to be designed) script creates a `patches/food_patch.json` template.
2.  The user edits the template.
3.  **`make patch-validate PATCH_TYPE=food`**: This runs the new `patch-apply-generic` target, which uses `apply_patch.py` to process the food patch.
4.  **`make patch-install PATCH_TYPE=food`**: Installs the patched save file.

This structure allows the `Makefile` to support any number of patch types without requiring new targets for each one.