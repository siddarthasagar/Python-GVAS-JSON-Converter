# Safe EotU Save File Modification Guide

## 🎯 Precise Value Control Strategy

### **Critical Understanding:**
- JSON files = **Analysis tool only**
- Real target = **Original .sav files**
- Process: `.sav → JSON → Modified .sav → Game`

## 🔧 Step-by-Step Safe Modification

### **1. Identify Exact Values**
```bash
# Get current values for analysis
make refresh && python patch_saves.py current
```

### **2. Create Targeted Patch**
```json
{
  "_description": "My Custom EotU Patch",
  "patches": {
    "Resources": 10000,        # Food storage: 67 → 10000
    "RoyalJelly": 9999,       # Royal jelly: 457 → 9999
    "Territory": null,         # Skip (null = don't modify)
    "Score": 50000,           # Boost score
    "TotalResourcesGathered": null,  # Skip lifetime stats
    "TilesExcavated": null    # Skip excavation count
  }
}
```

### **3. Apply with Safety Checks**
```bash
# Always backup first!
make backup

# Apply your specific patch
make patch PATCH=patches/my_custom_patch.json
```

## 🛡️ Game Corruption Prevention

### **Why .sav Files Get Corrupted:**
1. **Wrong data types** (string vs int)
2. **Invalid ranges** (negative values, too large numbers)
3. **Missing properties** (deleting required fields)
4. **Broken structure** (malformed binary)

### **Our Safety Measures:**
1. **Property-only modification** - Never delete, only change values
2. **Type preservation** - Keep same data type (int→int)
3. **Validation before apply** - Check structure integrity
4. **Automatic backups** - Always recoverable
5. **Incremental testing** - Small changes first

## 🎮 Recommended Testing Values

### **Conservative (Safe):**
```json
{
  "patches": {
    "Resources": 1000,     # 67 → 1000 (reasonable)
    "RoyalJelly": 1000     # 457 → 1000 (not extreme)
  }
}
```

### **Moderate:**
```json
{
  "patches": {
    "Resources": 5000,     # 67 → 5000
    "RoyalJelly": 5000,    # 457 → 5000
    "Score": 25000         # Boost score moderately
  }
}
```

### **Extreme (Test Last):**
```json
{
  "patches": {
    "Resources": 99999,    # Max resources
    "RoyalJelly": 99999,   # Max royal jelly
    "Score": 999999        # Max score
  }
}
```

## 🔍 Value Discovery Process

### **Finding New Properties:**
1. **Play game** → Make changes → Save
2. **Convert to JSON** → Compare before/after
3. **Identify new properties** → Add to patch template
4. **Test small changes first**

### **Example Discovery:**
```bash
# Before playing
python patch_saves.py current > before.txt

# Play game, make changes, save

# After playing  
make refresh && python patch_saves.py current > after.txt

# Compare
diff before.txt after.txt
```

## ⚠️ Critical Safety Rules

### **NEVER Modify:**
- Save file structure
- Property names  
- Data types
- Required game objects

### **ALWAYS:**
- Create backups first
- Test small changes
- Verify in-game before big changes
- Keep backups of working saves

### **IF CORRUPTION HAPPENS:**
```bash
# Immediate recovery
make restore

# Or specific backup
make restore-from
```

## 🎯 Precise Control Examples

### **Food Only:**
```json
{
  "patches": {
    "Resources": 2000
  }
}
```

### **Resources + Score:**
```json
{
  "patches": {
    "Resources": 5000,
    "Score": 30000
  }
}
```

### **Everything Except Lifetime Stats:**
```json
{
  "patches": {
    "Resources": 10000,
    "RoyalJelly": 9999,
    "Territory": 1000,
    "Score": 50000
  }
}
```

## 🚀 Quick Start Commands

```bash
# 1. Safety first
make backup

# 2. Get fresh data  
make refresh

# 3. Create template
make patch-template

# 4. Edit patches/patch_template.json with YOUR values

# 5. Apply safely
make patch PATCH=patches/patch_template.json

# 6. Test in game

# 7. If problems:
make restore
```
