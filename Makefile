.PHONY: format

format:
	-uvx isort . --skip-gitignore
	-uvx ruff format . --quiet
