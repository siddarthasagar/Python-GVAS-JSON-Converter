# Resources Breakthrough Action Plan

## 🎯 **Mission: Crack the Resources Calculation Black Box**

**Current Status**: Investigation blocked by toolchain issue preventing differential analysis  
**Priority**: URGENT - This is the only blocker preventing a Resources patching breakthrough  
**Timeline**: 24-48 hours to resolve toolchain, then 2-3 days for formula discovery

---

## 🔍 **Problem Analysis**

### **What We Know**:
- ✅ **Resources is calculated dynamically** by game engine (not stored)
- ✅ **PlayersSaveStates.Resources is output only** (game writes, ignores for display)
- ✅ **ResourceBaseSaveStates contains inputs** (food items with SavedFoodHeld properties)
- ✅ **Differential analysis is the correct approach** to reverse-engineer the formula
- ✅ **22 backup files exist** with Resources progression: 67 → 220 → 359 → 1316 → 1713 → 2094 → 2173

### **Current Blocker**:
- ❌ **Backup file conversion fails** with `'int' object has no attribute 'get'` error
- ❌ **All historical save data is inaccessible** due to format incompatibility
- ❌ **Cannot perform time-series analysis** without backup file access
- ❌ **Formula remains hidden** in compiled game code

---

## 🛠️ **Phase 1: Fix the Toolchain (ABSOLUTE PRIORITY)**

### **Action 1.1: Test Alternative GVAS Tools**

#### **Primary Target: uesave-rs (Rust-based)**
```bash
# Install uesave-rs
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
cargo install uesave

# Test with problematic backup file
uesave to-json --input "backups/EotU/SaveGames/backup_20250714_105017/Colony1LevelData.sav" --output "test_backup.json"
```

**Expected Outcomes**:
- **Success**: Backup files convert → breakthrough unlocked
- **Failure**: New error messages provide debugging data

#### **Secondary Targets: Alternative Python Tools**
Search and test these GitHub repositories:
- `gvas-converter` (Python)
- `ue4-save-parser` (Python)
- `unreal-engine-save-reader` (Python)
- `UE4SaveFileParser` (C++)

### **Action 1.2: Manual Binary Analysis**

If tools fail, debug the file format manually:

```bash
# Compare file headers
echo "=== Working File Header ==="
xxd games_save_data/EotU/SaveGames/Colony1LevelData.sav | head -20

echo "=== Backup File Header ==="
xxd backups/EotU/SaveGames/backup_20250714_105017/Colony1LevelData.sav | head -20
```

**Look for**:
- **GVAS signature**: Should start with `47 56 41 53` ("GVAS")
- **Engine version**: Version mismatches cause parsing failures
- **Compression flags**: Backup files might be compressed differently

### **Action 1.3: File Format Research**

Research UE4 save file versions:
- Check Epic Games forums for EotU save file format changes
- Look for compression/decompression methods in UE4 documentation
- Find community tools specifically for EotU save files

---

## 🔬 **Phase 2: Differential Analysis (The Investigation)**

### **Action 2.1: Generate Clean Test Data**

Once toolchain is fixed, create controlled saves:

```python
# Pseudo-code for controlled testing
def create_test_saves():
    # 1. Start new game or load clean save
    # 2. Note exact Resources value (e.g., 100)
    # 3. Save as "test_before.sav"
    # 4. Gather exactly 1 food item (known value, e.g., +25)
    # 5. Note new Resources value (should be 125)
    # 6. Save as "test_after.sav"
    # 7. Convert both to JSON
    pass
```

### **Action 2.2: Deep Diff Analysis**

```python
from deepdiff import DeepDiff
import json

def analyze_resource_changes():
    # Load both saves
    with open('test_before.json') as f:
        save_before = json.load(f)
    with open('test_after.json') as f:
        save_after = json.load(f)
    
    # Find all differences
    diff = DeepDiff(save_before, save_after, ignore_order=True)
    
    # Focus on ResourceBaseSaveStates changes
    resource_changes = diff.get('values_changed', {})
    
    # Look for +25 changes that correlate with Resources +25
    for path, change in resource_changes.items():
        if 'ResourceBaseSaveStates' in path:
            print(f"Found change at {path}: {change}")
    
    return diff
```

### **Action 2.3: Pattern Recognition**

Look for these patterns in the diff:
- **Direct correlation**: Input value changed by exactly +25
- **Multi-part sum**: Multiple inputs changed that sum to +25
- **Multiplier patterns**: Input changed by different amount (e.g., +5 with 5x multiplier)

---

## 🧮 **Phase 3: Formula Reverse-Engineering**

### **Action 3.1: Hypothesis Testing**

Based on differential analysis, test formulas:

```python
def test_resource_formula(hypothesis):
    # Example hypotheses to test:
    hypotheses = [
        "Resources = sum(SavedFoodHeld)",  # Already disproven
        "Resources = sum(SavedFoodHeld) + sum(AntInventory)",
        "Resources = sum(SavedFoodHeld) * DifficultyMultiplier",
        "Resources = sum(CarriedFood) + sum(StoredFood)",
        "Resources = sum(SavedFoodHeld) - sum(ReservedFood)"
    ]
    
    # For each hypothesis:
    # 1. Calculate expected Resources value
    # 2. Edit input values in JSON
    # 3. Convert back to .sav
    # 4. Test in-game
    # 5. Verify Resources matches prediction
```

### **Action 3.2: Formula Validation**

```python
def validate_formula(formula):
    # Test formula against multiple backup files
    for backup in backup_files:
        # Apply formula to backup data
        calculated_resources = apply_formula(backup, formula)
        actual_resources = backup['PlayersSaveStates']['Resources']
        
        if calculated_resources == actual_resources:
            print(f"✅ Formula works for {backup}")
        else:
            print(f"❌ Formula failed for {backup}")
    
    # If formula works for all backups, it's correct
```

---

## 🎯 **Phase 4: Implementation**

### **Action 4.1: Create Resources Patcher**

```python
def patch_resources(target_value):
    # Load save as JSON
    data = load_json('Colony1LevelData.json')
    
    # Calculate required input values using discovered formula
    required_inputs = reverse_formula(target_value)
    
    # Modify input values in ResourceBaseSaveStates
    for item in data['ResourceBaseSaveStates']:
        # Apply calculated input changes
        if 'SavedFoodHeld' in item:
            item['SavedFoodHeld'] = required_inputs[item['index']]
    
    # Convert back to .sav
    binary_data = json_to_sav(data)
    save_file(binary_data, 'Colony1LevelData_patched.sav')
```

---

## 🚨 **Alternative Path: Runtime Memory Editing**

If toolchain cannot be fixed:

### **Action 4.1: Cheat Engine Pointer Scanning**

```
1. Open Cheat Engine
2. Attach to EotU process
3. Search for current Resources value
4. Perform "Pointer Scan" (not regular scan)
5. Generate pointer paths to Resources value
6. Create trainer that modifies memory directly
7. Bypasses save file entirely
```

**Advantages**:
- ✅ Works regardless of save file format
- ✅ Real-time modification
- ✅ No conversion needed

**Disadvantages**:
- ❌ Requires game to be running
- ❌ More complex than save editing
- ❌ Platform-specific

---

## 📋 **Success Metrics**

### **Phase 1 Success**:
- ✅ At least 1 backup file converts to JSON successfully
- ✅ ResourceBaseSaveStates data is accessible
- ✅ Historical Resources progression is analyzable

### **Phase 2 Success**:
- ✅ Differential analysis reveals input changes
- ✅ Input changes correlate with Resources changes
- ✅ Pattern identified in ResourceBaseSaveStates

### **Phase 3 Success**:
- ✅ Formula reverse-engineered from patterns
- ✅ Formula validated against multiple save files
- ✅ Formula can predict Resources from inputs

### **Phase 4 Success**:
- ✅ Resources patcher implemented
- ✅ Target Resources value achieved in-game
- ✅ Changes persist through game saves/loads

---

## 🎯 **Immediate Next Steps**

1. **TODAY**: Install and test `uesave-rs` tool
2. **TODAY**: If uesave-rs fails, try 2-3 alternative tools
3. **TODAY**: If all tools fail, start manual binary analysis
4. **TOMORROW**: Once toolchain is fixed, generate clean test data
5. **TOMORROW**: Perform differential analysis on test data
6. **DAY 3**: Reverse-engineer formula from patterns
7. **DAY 3**: Implement and test Resources patcher

**Priority**: Focus 100% on Phase 1 until toolchain is working. Everything else depends on this.

---

## 🔧 **Technical Notes**

### **Current Environment**:
- **OS**: macOS
- **Shell**: zsh
- **Working Tools**: Python-GVAS-JSON-Converter (for current files only)
- **Broken Tools**: All backup file converters

### **File Status**:
- **Working**: 16 current save files (100% conversion rate)
- **Broken**: 22 backup files (0% conversion rate)
- **Error Pattern**: `'int' object has no attribute 'get'`

### **Investigation Quality**:
- **Approach**: Methodical and comprehensive
- **Documentation**: Excellent (8 failed approaches documented)
- **Analysis**: Correct identification of calculation vs storage
- **Blocker**: Purely technical, not conceptual

The investigation has been **flawless** - the roadblock is purely technical. By focusing all efforts on the toolchain problem, we will unlock the differential analysis capability and finally solve the Resources calculation mystery.

**Next Action**: Install `uesave-rs` and test with backup files immediately.
