## Brief overview
This guideline covers Makefile indentation rules for all future changes in this project. It ensures compatibility with GNU Make and prevents "missing separator" errors.

## Makefile indentation rules
- All command lines (recipes) under a target **must be indented with a single tab character**.
- **Never use spaces for indentation in recipes.**
- Variable assignments, target definitions, and comments **should not be indented**.
- If a Makefile error such as "missing separator" occurs, check for spaces instead of tabs in recipe lines.

## Example
```
target:
	@echo "This line is indented with a tab"
	@echo "So is this one"
```
**Do not use:**
```
target:
    @echo "This line is indented with spaces"   # ❌ Not allowed
```

## Application
- Always review Makefile changes for correct indentation before saving.
- Use editors or tools that preserve tab indentation for Makefile recipes.
- This rule applies to all Makefile updates, additions, and refactoring in this project.
