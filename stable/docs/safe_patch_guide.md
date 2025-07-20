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

## 🍯 Infinite Food Farm System

### **NEW: Resource Node Patching**
Create infinite renewable food sources by modifying resource nodes directly.

### **Step 1: Generate Food Nodes Template**
```bash
# Create inventory of all food sources
make food-nodes-template
```

This generates `patches/food_nodes_template.json` with all 885 resource nodes.

### **Step 2: Customize Food Sources**
Edit `patches/food_nodes_template.json`:
```json
{
  "description": "Food Nodes Patch Template",
  "nodes": [
    {
      "index": 42,
      "current_value": 15,
      "new_value": 999999,        # Set to infinite
      "resource_type": "EResourceType::Aphid",
      "enabled": true             # Enable this patch
    },
    {
      "index": 89,
      "current_value": 8,
      "new_value": 50000,
      "resource_type": "EResourceType::Seed",
      "enabled": true             # Enable this patch
    }
  ]
}
```

### **Step 3: Apply Food Node Patches**
```bash
# Apply your food node modifications
make patch-food-nodes PATCH=patches/food_nodes_template.json
```

### **Food Farm Strategies:**

#### **Conservative Approach:**
- Enable 5-10 high-value nodes
- Set to 2x-5x original values
- Focus on renewable sources (Aphids)

#### **Moderate Approach:**
- Enable 10-20 nodes
- Set to 10,000-50,000 food each
- Mix of resource types

#### **Infinite Farm:**
- Enable top 50 nodes
- Set all to 999,999 food
- Effectively unlimited resources

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

### **Standard Resource Patching:**
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

### **Infinite Food Farm Setup:**
```bash
# 1. Create backup
make backup

# 2. Generate food nodes template
make food-nodes-template

# 3. Edit patches/food_nodes_template.json
#    - Set "enabled": true for desired nodes
#    - Set "new_value" to desired amounts

# 4. Apply food node patches
make patch-food-nodes PATCH=patches/food_nodes_template.json

# 5. Convert back to .sav and test in game

# 6. If problems:
make restore
```

## 🎮 Complete Patching Workflows

### **Workflow 1: Quick Resource Boost**
```bash
make backup && make refresh && make quick-patch
```

### **Workflow 2: Custom Value Control**
```bash
make backup
make patch-template
# Edit patches/patch_template.json
make patch PATCH=patches/patch_template.json
```

### **Workflow 3: Infinite Food Farm**
```bash
make backup
make food-nodes-template
# Edit patches/food_nodes_template.json
make patch-food-nodes PATCH=patches/food_nodes_template.json
```

### **Workflow 4: Combined Approach**
```bash
make backup
# 1. Boost immediate resources
make patch-template && make patch PATCH=patches/patch_template.json
# 2. Create infinite food sources
make food-nodes-template && make patch-food-nodes PATCH=patches/food_nodes_template.json
```

## 🔧 Available Make Commands

### **File Management:**
- `make backup` - Create timestamped backup
- `make restore` - Restore from latest backup
- `make refresh` - Copy saves and convert to JSON
- `make status` - Show file status

### **Standard Patching:**
- `make patch-template` - Create patch template
- `make patch PATCH=file` - Apply patch file
- `make quick-patch` - Interactive patching

### **Food Node Patching:**
- `make food-nodes-template` - Create food nodes template
- `make patch-food-nodes PATCH=file` - Apply food nodes patch

### **Cleanup:**
- `make clean` - Remove local files (keeps backups)
- `make help` - Show all available commands
