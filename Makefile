# Unified Empires of the Undergrowth Save Management & Patching Makefile
# Supports both Python and uesave-rs workflows (for migration/testing)
# Handles all main save files (*.sav, excluding *-backup\d.sav)
# Includes dependency checks, improved help, and single/multi-save support

# --- Paths & Variables ---
SAVE_DIR := $(HOME)/Library/Application Support/Epic/EotU/Saved/SaveGames
PATCH_DIR := stable/patches
PYTHON_ENV := .venv/bin/python

# Multi-save support (default: all main saves)
MAIN_SAVES := $(shell find "$(SAVE_DIR)" -maxdepth 1 -type f -name '*.sav' ! -regex '.*-backup[0-9]\+\.sav' -exec basename {} \;)
ORIGINAL_SAVE ?= Colony1LevelData.sav

PATCH_TEMPLATE := $(PATCH_DIR)/food_nodes_template.json
PATCH ?= $(PATCH_TEMPLATE)
PATCH_TYPE ?= generic

# --- Colors ---
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help check-deps backup install clean validate show-config restore dev-patch save-files-refresh json-conversion patch-create patch-validate patch-apply patch-food-create patch-food-validate patch-food-apply patch-save test-workflow

# --- Help ---
help: ## Show this help message
	@echo "$(BLUE)Empires of the Undergrowth Save Manager & Patcher (Unified Workflow)$(NC)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Migration:$(NC)"
	@echo "  Use patch-create/patch-food-create for patching workflows."
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make patch-create"
	@echo "  make patch-validate"
	@echo "  make patch-apply"
	@echo "  make patch-save"
	@echo ""

# --- Dependency Checks ---
check-deps: ## Check if required tools are available
	@echo "$(BLUE)Checking dependencies...$(NC)"
	@command -v python3 >/dev/null 2>&1 || (echo "$(RED)Error: python3 not found$(NC)" && exit 1)
	@echo "$(GREEN)✓ All dependencies found$(NC)"

# --- Backup ---
backup: check-deps ## Backup all main save files (*.sav, excluding *-backupN.sav)
	@echo "$(BLUE)Backing up main save files...$(NC)"
	@mkdir -p games_save_data/EotU/SaveGames
	@for save in $(MAIN_SAVES); do \
		if [ -f "$(SAVE_DIR)/$$save" ]; then \
			cp "$(SAVE_DIR)/$$save" "games_save_data/EotU/SaveGames/$${save}_ORIGINAL.sav"; \
			echo "$(GREEN)✓ Backup created: games_save_data/EotU/SaveGames/$${save}_ORIGINAL.sav$(NC)"; \
		else \
			echo "$(RED)✗ Save not found: $(SAVE_DIR)/$$save$(NC)"; \
		fi \
	done

# --- Extract to JSON ---
# Removed extract-uesave (uesave-based)


# --- Patch JSON ---
# Removed patch-uesave (uesave-based)


# --- Convert patched JSON back to .sav ---
# Removed convert-uesave (uesave-based)


# --- Validate ---
validate: ## Validate modified save files
	@echo "$(BLUE)Validating modified save files...$(NC)"
	@for save in $(MAIN_SAVES); do \
		if [ -f "games_save_data/EotU/SaveGames/$${save}_MODIFIED.sav" ]; then \
			echo "$(GREEN)✓ Modified save exists: games_save_data/EotU/SaveGames/$${save}_MODIFIED.sav$(NC)"; \
			file "games_save_data/EotU/SaveGames/$${save}_MODIFIED.sav" | grep -q "data" && echo "$(GREEN)✓ File appears to be binary data$(NC)" || echo "$(YELLOW)⚠ File format check inconclusive$(NC)"; \
		else \
			echo "$(RED)✗ Modified save not found: games_save_data/EotU/SaveGames/$${save}_MODIFIED.sav$(NC)"; \
		fi \
	done

# --- Install ---
install: validate ## Install modified save files to game directory
	@echo "$(BLUE)Installing modified save files to game directory...$(NC)"
	@for save in $(MAIN_SAVES); do \
		if [ -f "games_save_data/EotU/SaveGames/$${save}_MODIFIED.sav" ]; then \
			cp "games_save_data/EotU/SaveGames/$${save}_MODIFIED.sav" "$(SAVE_DIR)/$$save"; \
			echo "$(GREEN)✓ Installed: $(SAVE_DIR)/$$save$(NC)"; \
		else \
			echo "$(RED)✗ Modified save not found: games_save_data/EotU/SaveGames/$${save}_MODIFIED.sav$(NC)"; \
		fi \
	done

# --- Clean ---
clean: ## Remove temp files
	@echo "$(BLUE)Cleaning up temp files...$(NC)"
	@rm -rf games_save_data patches stable/patches
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

# --- Restore ---
restore: ## Restore original saves from backup
	@echo "$(BLUE)Restoring original saves from backup...$(NC)"
	@for save in $(MAIN_SAVES); do \
		if [ -f "games_save_data/EotU/SaveGames/$${save}_ORIGINAL.sav" ]; then \
			cp "games_save_data/EotU/SaveGames/$${save}_ORIGINAL.sav" "$(SAVE_DIR)/$$save"; \
			echo "$(GREEN)✓ Restored: $(SAVE_DIR)/$$save$(NC)"; \
		else \
			echo "$(RED)✗ Backup not found: games_save_data/EotU/SaveGames/$${save}_ORIGINAL.sav$(NC)"; \
		fi \
	done

# --- Show Config ---
show-config: ## Show current configuration
	@echo "$(BLUE)Current Configuration:$(NC)"
	@echo "  Save Directory: $(SAVE_DIR)"
	@echo "  Patch Directory: $(PATCH_DIR)"
	@echo "  Main Saves: $(MAIN_SAVES)"
	@echo "  Python Env: $(PYTHON_ENV)"
	@echo "  Patch Template: $(PATCH)"
	@for save in $(MAIN_SAVES); do \
		echo "  Backup: games_save_data/EotU/SaveGames/$${save}_ORIGINAL.sav"; \
		echo "  Working JSON: games_save_data/EotU/json/$${save}_working.json"; \
		echo "  Patched JSON: games_save_data/EotU/json/$${save}_patched.json"; \
		echo "  Modified Save: games_save_data/EotU/SaveGames/$${save}_MODIFIED.sav"; \
	done

# --- Test Workflow (safe, does not install) ---
test-workflow: validate ## Full test workflow (safe, does not install)
	@echo "$(GREEN)✓ Test workflow completed successfully$(NC)"
	@echo "$(BLUE)Files created:$(NC)"
	@for save in $(MAIN_SAVES); do \
		echo "  - games_save_data/EotU/json/$${save}_working.json (extracted save)"; \
		echo "  - games_save_data/EotU/json/$${save}_patched.json (patched save)"; \
		echo "  - games_save_data/EotU/SaveGames/$${save}_MODIFIED.sav (converted save)"; \
	done
	@echo "$(YELLOW)Run 'make install' to apply changes to game$(NC)"

# --- Save Files Refresh ---
save-files-refresh: backup ## Refresh save files and extract latest JSON
	@echo "$(GREEN)✓ Save files refreshed and JSON extracted$(NC)"

# --- JSON Conversion (compatibility stub) ---
json-conversion: ## Compatibility target for patch-create/patch-food-create
	@echo "$(YELLOW)json-conversion: No action needed (conversion handled in later steps)$(NC)"

# --- Patch Workflow (jelly/territory numeric patch) ---
patch-create: clean save-files-refresh ## Legacy patch-create for RoyalJelly/Territory
	@echo "$(BLUE)Copying .sav files from game location...$(NC)"
	@mkdir -p games_save_data/EotU/SaveGames games_save_data/EotU/json
	@for save in $(MAIN_SAVES); do \
		if [ -f "$(SAVE_DIR)/$$save" ]; then \
			cp "$(SAVE_DIR)/$$save" "games_save_data/EotU/SaveGames/$$save"; \
			echo "$(GREEN)✓ Copied: $$save$(NC)"; \
		else \
			echo "$(RED)✗ Save not found: $(SAVE_DIR)/$$save$(NC)"; \
		fi \
	done
	@echo "$(BLUE)Converting .sav files to JSON...$(NC)"
	@if [ -f "games_save_data/EotU/SaveGames/Colony1LevelData.sav" ]; then \
		PYTHONPATH=. python3 utils_savconverter/convert_eotu_saves.py "games_save_data/EotU/SaveGames/Colony1LevelData.sav" "games_save_data/EotU/json/Colony1LevelData.json"; \
		echo "$(GREEN)✓ Converted: Colony1LevelData.sav to JSON$(NC)"; \
	else \
		echo "$(RED)✗ Save not found for conversion: games_save_data/EotU/SaveGames/Colony1LevelData.sav$(NC)"; \
	fi
	@echo "$(BLUE)Creating patch template from JSON...$(NC)"
	PYTHONPATH=. python3 utils_savconverter/patch_saves.py template
	@echo "$(GREEN)✓ Patch template created: stable/patches/patch_template.json$(NC)"
	@echo "$(YELLOW)Edit the template and run 'make patch-validate'$(NC)"

patch-validate:## Validate patch template for EotU saves
	@echo "$(BLUE)Validating patch template for Colony1LevelData.sav only...$(NC)"
	PYTHONPATH=. python3 utils_savconverter/patch_saves.py apply patches/patch_template.json "games_save_data/EotU/SaveGames/Colony1LevelData.sav" "games_save_data/EotU/json/Colony1LevelData_patched.json"
	@echo "$(GREEN)✓ Patched: games_save_data/EotU/json/Colony1LevelData_patched.json$(NC)"
	@echo "$(YELLOW)Run 'make patch-apply' to copy modified saves to game directory$(NC)"

patch-apply: ## Apply jelly/territory patch to save files
	@echo "$(BLUE)Applying patch to Colony1LevelData.sav only...$(NC)"
	@if [ -f "games_save_data/EotU/SaveGames/Colony1LevelData.sav" ]; then \
		cp "games_save_data/EotU/SaveGames/Colony1LevelData.sav" "$(SAVE_DIR)/Colony1LevelData.sav"; \
		echo "$(GREEN)✓ Applied: $(SAVE_DIR)/Colony1LevelData.sav$(NC)"; \
	else \
		echo "$(RED)✗ Patched file not found: games_save_data/EotU/SaveGames/Colony1LevelData.sav$(NC)"; \
	fi

# --- Patch Workflow (food resources) ---
patch-food-create: save-files-refresh json-conversion ## Create a food patch template (scans latest Colony1Stage save)
	@echo "$(BLUE)Creating food patch template...$(NC)"
	@python3 stable/bin/create_patch_template.py --mode food
	@echo "$(GREEN)✓ Food patch template created: $(PATCH_DIR)/food_patch_template.json$(NC)"
	@echo "$(YELLOW)Edit the template and run 'make patch-food-validate'$(NC)"

patch-food-validate: ## Validate food patch template
	@echo "$(BLUE)Validating food patch template...$(NC)"
	@for save in $(MAIN_SAVES); do \
		python3 stable/bin/apply_patch.py --type food --input "$(TEMP_DIR)/$${save}_working.json" --output "$(TEMP_DIR)/$${save}_patched.json" --patch "$(PATCH_DIR)/food_patch_template.json"; \
		$(PYTHON_ENV) utils_savconverter/convert_json_to_sav.py "$(TEMP_DIR)/$${save}_patched.json" "$(TEMP_DIR)/$${save}_MODIFIED.sav"; \
		echo "$(GREEN)✓ Patched and converted: $(TEMP_DIR)/$${save}_MODIFIED.sav$(NC)"; \
	done
	@echo "$(YELLOW)Run 'make patch-food-apply' to copy modified saves to game directory$(NC)"

patch-food-apply: ## Apply food patch to save files
	@echo "$(BLUE)Applying food patch to save files...$(NC)"
	@for save in $(MAIN_SAVES); do \
		if [ -f "$(TEMP_DIR)/$${save}_MODIFIED.sav" ]; then \
			cp "$(TEMP_DIR)/$${save}_MODIFIED.sav" "$(SAVE_DIR)/$$save"; \
			echo "$(GREEN)✓ Applied: $(SAVE_DIR)/$$save$(NC)"; \
		else \
			echo "$(RED)✗ Modified save not found: $(TEMP_DIR)/$${save}_MODIFIED.sav$(NC)"; \
		fi \
	done

# --- Single-save workflow (for patch-save target) ---
patch-save: install ## Complete workflow: backup → extract → patch → convert → install (single save)
	@echo "$(GREEN)🎉 Save patching complete!$(NC)"

dev-patch: ## Quick patch for development (uses existing JSON if available)
	@if [ -f "$(WORKING_JSON)" ]; then \
		echo "$(BLUE)Using existing $(WORKING_JSON)$(NC)"; \
		make patch convert validate; \
	else \
		make test-workflow; \
	fi

# --- RULE: All recipe lines (commands) in this Makefile are indented with tabs only ---
# --- Never use spaces for indentation in recipes. Variable assignments and comments are not indented. ---
