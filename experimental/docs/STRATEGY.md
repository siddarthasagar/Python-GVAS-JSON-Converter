# Safe EotU Save Patching Strategy

## 🎯 **Working Properties (Safe to Patch)**
- ✅ **Territory**: Controls territory expansion 
- ✅ **RoyalJelly**: Royal jelly resource count
- ✅ **Score**: Player score
- ✅ **TotalResourcesGathered**: Lifetime resource total
- ✅ **TilesExcavated**: Total tiles dug

## ❌ **Problematic Properties (Avoid)**
- ❌ **Resources**: Causes file corruption - avoid patching

## 🚀 **Recommended Patching Approach**

### **Conservative Patching (Recommended)**
Focus on non-critical but fun properties:
```json
{
  "patches": {
    "Territory": 1000,           # Expand territory
    "Score": 50000,             # Boost score
    "TotalResourcesGathered": 25000,  # Boost lifetime total
    "TilesExcavated": 2000      # Increase excavation count
  }
}
```

### **RoyalJelly Boost (If Needed)**
```json
{
  "patches": {
    "RoyalJelly": 5000          # Increase royal jelly
  }
}
```

### **Territory Focus (Most Visible)**
```json
{
  "patches": {
    "Territory": 2000           # Massive territory expansion
  }
}
```

## 🔍 **Why Resources is Problematic**

### **Possible Reasons:**
1. **Validation Logic**: Game validates Resources against max capacity
2. **Calculated Property**: Resources might be calculated from other values
3. **Complex Dependencies**: Resources depends on colony size, upgrades, etc.
4. **Checksum Protection**: Game has corruption detection for Resources

### **Alternative Approaches for Resources:**
1. **Find the capacity value** and increase that first
2. **Look for nest upgrades** that increase food storage
3. **Focus on indirect boosts** (Territory → more gathering → more resources)

## 🎮 **Recommended Workflow**

### **Safe Testing Sequence:**
```bash
# 1. Always backup first
make backup

# 2. Get fresh data
make refresh

# 3. Test single property first
# Edit patch_template.json with ONE property
make patch PATCH=patches/patch_template.json

# 4. Test in game
make copy-to-original
# Launch game and verify

# 5. If it works, try combinations
```

### **Property Priority Order:**
1. **Territory** (most visible, safest)
2. **Score** (fun, harmless)  
3. **RoyalJelly** (useful resource)
4. **TotalResourcesGathered** (background stat)
5. **TilesExcavated** (background stat)

## 🎯 **Next Steps**

### **Immediate Actions:**
1. **Test Territory patching** (known to work)
2. **Avoid Resources entirely** for now
3. **Focus on working properties** for actual gameplay benefit

### **Research Directions:**
1. **Find food capacity properties** (MaxResources, StorageCapacity, etc.)
2. **Look for nest upgrade properties** (colony size, storage upgrades)
3. **Search for food generation rates** (gathering speed, efficiency)

### **Long-term Goals:**
1. **Reverse engineer Resources dependencies**
2. **Find the root cause of corruption**
3. **Develop Resources-specific patching approach**

## 🏆 **Success Metrics**

You've already achieved:
- ✅ **Complete save file analysis** and understanding
- ✅ **Working JSON conversion** system
- ✅ **Safe backup/restore** infrastructure  
- ✅ **Multiple property patching** (Territory, RoyalJelly, Score)
- ✅ **Automated workflow** with Makefile

**Focus on exploiting what works rather than fixing what's broken!**
