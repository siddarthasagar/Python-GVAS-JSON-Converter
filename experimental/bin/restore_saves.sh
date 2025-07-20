#!/bin/bash
# Restore Original Save Files After Testing

echo "🔄 Restoring Original Save Files"
echo "==============================="

GAME_SAVE_PATH="$HOME/Library/Application Support/Epic/EotU/Saved/SaveGames"
BACKUP_DIR="backups/EotU/SaveGames/pre_test_20250715_104109"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory not found: $BACKUP_DIR"
    echo "Please check the backup location or restore manually."
    exit 1
fi

echo "📂 Restoring from: $BACKUP_DIR"
echo "📂 Restoring to: $GAME_SAVE_PATH"

# Restore the backup files
cp "$BACKUP_DIR"/*.sav "$GAME_SAVE_PATH/"

echo "✅ Original save files restored!"
echo ""
echo "🎮 You can now safely continue your normal game."
echo "The test modifications have been removed."
