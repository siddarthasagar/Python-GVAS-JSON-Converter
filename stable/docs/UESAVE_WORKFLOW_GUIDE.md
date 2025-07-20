# Empires of the Undergrowth Save Management & Patching Workflow Guide

## Overview

This guide describes the **unified workflow** for managing, patching, and restoring Empires of the Undergrowth save files using the consolidated Makefile.  
It supports both the new `uesave-rs` tool and legacy Python scripts for migration/testing.  
All operations work on main save files (`*.sav`), **excluding** any files matching `*-backupN.sav`.

---

## File Structure

- **Game Save Directory:**  
  `~/Library/Application Support/Epic/EotU/Saved/SaveGames`
- **Temp Directory:**  
  `./temp`
- **Patch Directory:**  
  `./patches`
- **Python Virtualenv:**  
  `./.venv/bin/python` (for legacy scripts)

---

## Main Save Files

All files matching `*.sav` in the save directory, **excluding** any files matching `*-backupN.sav`.

---

## Workflow Commands

### 1. **Backup Main Save Files**
```sh
make backup
```
- Copies all main save files to `./temp/` as `<filename>_ORIGINAL.sav`.

---

### 2. **Extract Save Files to JSON**

#### Using uesave-rs (recommended):
```sh
make extract-uesave
```
- Converts each backup save to JSON: `<filename>_working.json` in `./temp/`.

#### Using Python scripts (legacy):
```sh
make extract-py
```
- Converts each backup save to JSON using Python.

---

### 3. **Patch JSON Files**

#### Using uesave-rs format patcher:
```sh
make patch-uesave PATCH=patches/my_patch.json
```
- Applies patch template to each JSON file, producing `<filename>_patched.json`.

#### Using Python scripts (legacy):
```sh
make patch-py PATCH=patches/my_patch.json
```
- Applies patch using legacy Python scripts.

---

### 4. **Convert Patched JSON Back to Save Files**

#### Using uesave-rs:
```sh
make convert-uesave
```
- Converts each patched JSON to `<filename>_MODIFIED.sav`.

#### Using Python scripts (legacy):
```sh
make convert-py
```
- Converts each patched JSON to `<filename>_MODIFIED.sav` using Python.

---

### 5. **Validate Modified Save Files**
```sh
make validate
```
- Checks existence and basic format of all modified save files.

---

### 6. **Install Modified Save Files to Game Directory**
```sh
make install
```
- Copies all modified save files to the game save directory, overwriting originals.

---

### 7. **Restore Original Save Files from Backup**
```sh
make restore
```
- Restores original saves from backup in `./temp/`.

---

### 8. **Clean Temporary Files**
```sh
make clean
```
- Removes all temp files.

---

### 9. **Show Current Configuration**
```sh
make show-config
```
- Displays all paths, main save files, and patch template in use.

---

### 10. **Test Full Workflow (Safe)**
```sh
make test-workflow
```
- Runs backup, extract, patch, convert, and validate steps **without installing**.

---

## Patch Template

- Patch templates should be placed in `./patches/`.
- Example usage:  
  `make patch-uesave PATCH=patches/food_nodes_template.json`
- The patcher will only modify values, never structure.

---

## Notes

- **Backup/restore only affects main save files (`*.sav`), not backup variants (`*-backupN.sav`).**
- You can safely migrate from Python to uesave-rs by using the respective commands.
- All temp and patch files are organized for easy cleanup and tracking.

---

## Quick Reference

| Step         | Command (uesave-rs)           | Command (Python legacy)      |
|--------------|------------------------------|------------------------------|
| Backup       | `make backup`                | `make backup`                |
| Extract      | `make extract-uesave`        | `make extract-py`            |
| Patch        | `make patch-uesave PATCH=...`| `make patch-py PATCH=...`    |
| Convert      | `make convert-uesave`        | `make convert-py`            |
| Validate     | `make validate`              | `make validate`              |
| Install      | `make install`               | `make install`               |
| Restore      | `make restore`               | `make restore`               |
| Clean        | `make clean`                 | `make clean`                 |
| Show Config  | `make show-config`           | `make show-config`           |
| Test         | `make test-workflow`         | `make test-workflow`         |

---

## Troubleshooting

- If you see missing files, check the save directory and patch template paths.
- For migration, test both workflows before removing Python support.

---

## Maintainer Notes

- Update this guide if you add new patch types or change directory structure.
- Remove Python commands once migration to uesave-rs is complete.

---
