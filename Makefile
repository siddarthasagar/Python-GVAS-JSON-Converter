# Empires of the Undergrowth Save File Management
# Makefile for copying save files and converting to JSON

# Paths
ORIGINAL_SAVES_PATH = $(HOME)/Library/Application Support/Epic/EotU/Saved/SaveGames
LOCAL_SAVES_PATH = games_save_data/EotU/SaveGames
JSON_OUTPUT_PATH = games_save_data/EotU/json
BACKUP_PATH = backups/EotU/SaveGames
PYTHON_ENV = .venv/bin/python

# Generate timestamp for backups
TIMESTAMP = $(shell date +"%Y%m%d_%H%M%S")

# Default target
.PHONY: all
all: copy-saves convert-json

# Task: Create backup of original save files
.PHONY: backup
backup:
	@echo "💾 Creating backup of original save files..."
	@echo "Source: $(ORIGINAL_SAVES_PATH)"
	@echo "Target: $(BACKUP_PATH)/backup_$(TIMESTAMP)"
	@# Check if original saves exist
	@if [ ! -d "$(ORIGINAL_SAVES_PATH)" ]; then \
		echo "❌ Original saves directory not found: $(ORIGINAL_SAVES_PATH)"; \
		echo "💡 Make sure Empires of the Undergrowth has been run and saves exist"; \
		exit 1; \
	fi
	@# Create backup directory structure
	@mkdir -p "$(BACKUP_PATH)/backup_$(TIMESTAMP)"
	@# Copy save files with timestamp
	@echo "📁 Creating timestamped backup..."
	@cp -R "$(ORIGINAL_SAVES_PATH)/"* "$(BACKUP_PATH)/backup_$(TIMESTAMP)/"
	@echo "✅ Backup created successfully!"
	@echo "📊 Backup location: $(BACKUP_PATH)/backup_$(TIMESTAMP)"
	@echo "📊 Files backed up:"
	@ls -la "$(BACKUP_PATH)/backup_$(TIMESTAMP)" | head -10
	@# Create/update 'latest' symlink for easy access
	@if [ -L "$(BACKUP_PATH)/latest" ]; then \
		rm "$(BACKUP_PATH)/latest"; \
	fi
	@ln -s "backup_$(TIMESTAMP)" "$(BACKUP_PATH)/latest"
	@echo "🔗 Latest backup symlink updated: $(BACKUP_PATH)/latest"

# Task: Restore from latest backup
.PHONY: restore
restore:
	@echo "🔄 Restoring save files from latest backup..."
	@# Check if backup exists
	@if [ ! -L "$(BACKUP_PATH)/latest" ]; then \
		echo "❌ No backup found. Available backups:"; \
		if [ -d "$(BACKUP_PATH)" ]; then \
			ls -la "$(BACKUP_PATH)" | grep "backup_" || echo "No backups available"; \
		else \
			echo "No backup directory found"; \
		fi; \
		echo "💡 Run 'make backup' first to create a backup"; \
		exit 1; \
	fi
	@echo "Source: $(BACKUP_PATH)/latest"
	@echo "Target: $(ORIGINAL_SAVES_PATH)"
	@# Confirm restore operation
	@echo "⚠️  This will OVERWRITE your current save files!"
	@echo "📁 Backup source: $$(readlink "$(BACKUP_PATH)/latest")"
	@read -p "Are you sure you want to restore? (y/N): " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "❌ Restore cancelled"; \
		exit 1; \
	fi
	@# Create backup of current state before restore
	@echo "💾 Creating safety backup of current state..."
	@mkdir -p "$(BACKUP_PATH)/pre_restore_$(TIMESTAMP)"
	@if [ -d "$(ORIGINAL_SAVES_PATH)" ]; then \
		cp -R "$(ORIGINAL_SAVES_PATH)/"* "$(BACKUP_PATH)/pre_restore_$(TIMESTAMP)/" 2>/dev/null || true; \
	fi
	@# Perform restore
	@echo "🔄 Restoring files..."
	@rm -rf "$(ORIGINAL_SAVES_PATH)"
	@mkdir -p "$$(dirname "$(ORIGINAL_SAVES_PATH)")"
	@cp -R "$(BACKUP_PATH)/latest" "$(ORIGINAL_SAVES_PATH)"
	@echo "✅ Restore completed successfully!"
	@echo "📊 Files restored:"
	@ls -la "$(ORIGINAL_SAVES_PATH)" | head -10
	@echo "💾 Pre-restore backup saved to: $(BACKUP_PATH)/pre_restore_$(TIMESTAMP)"

# Task: Restore from specific backup
.PHONY: restore-from
restore-from:
	@echo "📋 Available backups:"
	@if [ -d "$(BACKUP_PATH)" ]; then \
		ls -la "$(BACKUP_PATH)" | grep "backup_" | awk '{print "  " $$9 " (" $$6 " " $$7 " " $$8 ")"}' || echo "No backups available"; \
	else \
		echo "No backup directory found"; \
		exit 1; \
	fi
	@echo ""
	@read -p "Enter backup name (e.g., backup_20250714_143022): " backup_name; \
	if [ ! -d "$(BACKUP_PATH)/$$backup_name" ]; then \
		echo "❌ Backup not found: $$backup_name"; \
		exit 1; \
	fi; \
	echo "🔄 Restoring from: $$backup_name"; \
	echo "⚠️  This will OVERWRITE your current save files!"; \
	read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "❌ Restore cancelled"; \
		exit 1; \
	fi; \
	echo "💾 Creating safety backup of current state..."; \
	mkdir -p "$(BACKUP_PATH)/pre_restore_$(TIMESTAMP)"; \
	if [ -d "$(ORIGINAL_SAVES_PATH)" ]; then \
		cp -R "$(ORIGINAL_SAVES_PATH)/"* "$(BACKUP_PATH)/pre_restore_$(TIMESTAMP)/" 2>/dev/null || true; \
	fi; \
	echo "🔄 Restoring files..."; \
	rm -rf "$(ORIGINAL_SAVES_PATH)"; \
	mkdir -p "$$(dirname "$(ORIGINAL_SAVES_PATH)")"; \
	cp -R "$(BACKUP_PATH)/$$backup_name/"* "$(ORIGINAL_SAVES_PATH)/"; \
	echo "✅ Restore completed successfully!"; \
	echo "📊 Files restored from: $$backup_name"; \
	echo "💾 Pre-restore backup saved to: $(BACKUP_PATH)/pre_restore_$(TIMESTAMP)"

# Task: List all backups
.PHONY: list-backups
list-backups:
	@echo "📋 Available Backups"
	@echo "==================="
	@if [ -d "$(BACKUP_PATH)" ]; then \
		echo "Backup location: $(BACKUP_PATH)"; \
		echo ""; \
		if [ -L "$(BACKUP_PATH)/latest" ]; then \
			echo "🔗 Latest: $$(readlink "$(BACKUP_PATH)/latest")"; \
			echo ""; \
		fi; \
		echo "All backups:"; \
		ls -la "$(BACKUP_PATH)" | grep "backup_" | while read -r line; do \
			backup_name=$$(echo "$$line" | awk '{print $$9}'); \
			backup_date=$$(echo "$$line" | awk '{print $$6 " " $$7 " " $$8}'); \
			file_count=$$(ls "$(BACKUP_PATH)/$$backup_name" 2>/dev/null | wc -l | tr -d ' '); \
			echo "  📁 $$backup_name ($$backup_date) - $$file_count files"; \
		done; \
		if [ $$(ls "$(BACKUP_PATH)" | grep -c "backup_") -eq 0 ]; then \
			echo "No backups found"; \
		fi; \
	else \
		echo "No backup directory found"; \
		echo "💡 Run 'make backup' to create your first backup"; \
	fi

# Task 1: Copy saved files from original location
.PHONY: copy-saves
copy-saves:
	@echo "🔄 Copying save files from original location..."
	@echo "Source: $(ORIGINAL_SAVES_PATH)"
	@echo "Target: $(LOCAL_SAVES_PATH)"
	@# Remove existing local saves directory if it exists
	@if [ -d "$(LOCAL_SAVES_PATH)" ]; then \
		echo "🗑️  Removing existing local saves directory..."; \
		rm -rf "$(LOCAL_SAVES_PATH)"; \
	fi
	@# Create parent directory structure
	@mkdir -p games_save_data/EotU
	@# Copy entire SaveGames folder from original location
	@if [ -d "$(ORIGINAL_SAVES_PATH)" ]; then \
		echo "📁 Copying save files..."; \
		cp -R "$(ORIGINAL_SAVES_PATH)" "$(LOCAL_SAVES_PATH)"; \
		echo "✅ Save files copied successfully!"; \
		echo "📊 Files copied:"; \
		ls -la "$(LOCAL_SAVES_PATH)" | head -10; \
	else \
		echo "❌ Original saves directory not found: $(ORIGINAL_SAVES_PATH)"; \
		echo "💡 Make sure Empires of the Undergrowth has been run and saves exist"; \
		exit 1; \
	fi

# Task 2: Convert saves to JSON
.PHONY: convert-json
convert-json:
	@echo "🔄 Converting save files to JSON format..."
	@echo "Target: $(JSON_OUTPUT_PATH)"
	@# Check if saves exist locally
	@if [ ! -d "$(LOCAL_SAVES_PATH)" ]; then \
		echo "❌ Local saves directory not found: $(LOCAL_SAVES_PATH)"; \
		echo "💡 Run 'make copy-saves' first to copy the save files"; \
		exit 1; \
	fi
	@# Remove existing JSON directory if it exists
	@if [ -d "$(JSON_OUTPUT_PATH)" ]; then \
		echo "🗑️  Removing existing JSON directory..."; \
		rm -rf "$(JSON_OUTPUT_PATH)"; \
	fi
	@# Create JSON output directory
	@mkdir -p "$(JSON_OUTPUT_PATH)"
	@# Run the conversion script
	@echo "🔧 Running conversion script..."
	@if [ -f "$(PYTHON_ENV)" ]; then \
		$(PYTHON_ENV) convert_eotu_saves.py; \
	else \
		echo "❌ Python virtual environment not found: $(PYTHON_ENV)"; \
		echo "💡 Make sure you have set up the virtual environment"; \
		exit 1; \
	fi
	@echo "✅ JSON conversion completed!"
	@echo "📊 JSON files created:"
	@ls -la "$(JSON_OUTPUT_PATH)" | head -10

# Task 3: Full refresh - copy saves and convert to JSON
.PHONY: refresh
refresh: copy-saves convert-json
	@echo "🎉 Full refresh completed!"
	@echo "✅ Save files copied from original location"
	@echo "✅ JSON conversion completed"
	@echo "📁 Local saves: $(LOCAL_SAVES_PATH)"
	@echo "📁 JSON files: $(JSON_OUTPUT_PATH)"

# Clean up local files (keeps original saves and backups untouched)
.PHONY: clean
clean:
	@echo "🧹 Cleaning up local save files and JSON..."
	@if [ -d "$(LOCAL_SAVES_PATH)" ]; then \
		echo "🗑️  Removing local saves: $(LOCAL_SAVES_PATH)"; \
		rm -rf "$(LOCAL_SAVES_PATH)"; \
	fi
	@if [ -d "$(JSON_OUTPUT_PATH)" ]; then \
		echo "🗑️  Removing JSON files: $(JSON_OUTPUT_PATH)"; \
		rm -rf "$(JSON_OUTPUT_PATH)"; \
	fi
	@echo "✅ Cleanup completed!"
	@echo "💡 Original saves and backups remain untouched"

# Clean up old backups (keeps last 5)
.PHONY: clean-old-backups
clean-old-backups:
	@echo "🧹 Cleaning up old backups (keeping last 5)..."
	@if [ -d "$(BACKUP_PATH)" ]; then \
		backup_count=$$(ls "$(BACKUP_PATH)" | grep -c "backup_" || echo 0); \
		if [ $$backup_count -gt 5 ]; then \
			echo "📊 Found $$backup_count backups, removing oldest..."; \
			ls -t "$(BACKUP_PATH)"/backup_* | tail -n +6 | xargs rm -rf; \
			echo "✅ Old backups cleaned up"; \
		else \
			echo "📊 Found $$backup_count backups (≤5), no cleanup needed"; \
		fi; \
	else \
		echo "No backup directory found"; \
	fi

# Show status of files
.PHONY: status
status:
	@echo "📊 EotU Save Files Status"
	@echo "========================="
	@echo "Original saves location: $(ORIGINAL_SAVES_PATH)"
	@if [ -d "$(ORIGINAL_SAVES_PATH)" ]; then \
		echo "✅ Original saves found ($(shell ls "$(ORIGINAL_SAVES_PATH)" | wc -l | tr -d ' ') files)"; \
		echo "📅 Last modified: $(shell stat -f "%Sm" "$(ORIGINAL_SAVES_PATH)" 2>/dev/null || echo "unknown")"; \
	else \
		echo "❌ Original saves not found"; \
	fi
	@echo ""
	@echo "Local saves location: $(LOCAL_SAVES_PATH)"
	@if [ -d "$(LOCAL_SAVES_PATH)" ]; then \
		echo "✅ Local saves found ($(shell ls "$(LOCAL_SAVES_PATH)" | wc -l | tr -d ' ') files)"; \
		echo "📅 Last modified: $(shell stat -f "%Sm" "$(LOCAL_SAVES_PATH)" 2>/dev/null || echo "unknown")"; \
	else \
		echo "❌ Local saves not found"; \
	fi
	@echo ""
	@echo "JSON files location: $(JSON_OUTPUT_PATH)"
	@if [ -d "$(JSON_OUTPUT_PATH)" ]; then \
		echo "✅ JSON files found ($(shell ls "$(JSON_OUTPUT_PATH)" | wc -l | tr -d ' ') files)"; \
		echo "📅 Last modified: $(shell stat -f "%Sm" "$(JSON_OUTPUT_PATH)" 2>/dev/null || echo "unknown")"; \
	else \
		echo "❌ JSON files not found"; \
	fi
	@echo ""
	@echo "Backup location: $(BACKUP_PATH)"
	@if [ -d "$(BACKUP_PATH)" ]; then \
		backup_count=$(shell ls "$(BACKUP_PATH)" 2>/dev/null | grep -c "backup_" || echo 0); \
		echo "✅ Backup directory found ($$backup_count backups)"; \
		if [ -L "$(BACKUP_PATH)/latest" ]; then \
			echo "🔗 Latest backup: $(shell readlink "$(BACKUP_PATH)/latest")"; \
		fi; \
	else \
		echo "❌ No backups found"; \
		echo "💡 Run 'make backup' to create your first backup"; \
	fi

# Help target
.PHONY: help
help:
	@echo "🎮 Empires of the Undergrowth Save File Manager"
	@echo "=============================================="
	@echo ""
	@echo "📁 File Management:"
	@echo "  copy-saves       - Copy save files from original location to local project"
	@echo "  convert-json     - Convert local save files to JSON format"
	@echo "  refresh          - Full refresh: copy saves + convert to JSON"
	@echo ""
	@echo "💾 Backup & Recovery:"
	@echo "  backup           - Create timestamped backup of original save files"
	@echo "  restore          - Restore from latest backup (with confirmation)"
	@echo "  restore-from     - Restore from specific backup (interactive)"
	@echo "  list-backups     - List all available backups with details"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  clean            - Remove local saves and JSON files (keeps originals & backups)"
	@echo "  clean-old-backups- Remove old backups (keeps last 5)"
	@echo ""
	@echo "📊 Information:"
	@echo "  status           - Show status of save files in all locations"
	@echo "  help             - Show this help message"
	@echo ""
	@echo "🚨 Safety Workflow for Save Modification:"
	@echo "  1. make backup          # Create safety backup"
	@echo "  2. make copy-saves      # Get local copy for editing"
	@echo "  3. make convert-json    # Convert to JSON for modification"
	@echo "  4. [Edit JSON files]    # Make your changes"
	@echo "  5. [Convert back & test]# Test your modifications"
	@echo "  6. make restore         # If something goes wrong"
	@echo ""
	@echo "📂 File locations:"
	@echo "  Original: $(ORIGINAL_SAVES_PATH)"
	@echo "  Local:    $(LOCAL_SAVES_PATH)"
	@echo "  JSON:     $(JSON_OUTPUT_PATH)"
	@echo "  Backups:  $(BACKUP_PATH)"
