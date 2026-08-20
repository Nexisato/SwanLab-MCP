.PHONY: format clean

format:
	-uvx isort . --skip-gitignore
	-uvx ruff format . --quiet

# 清理构建产物与工具缓存（不影响 .venv / playground / uv.lock）
clean:
	rm -rf dist build wheels *.egg-info src/*.egg-info
	rm -rf .ruff_cache .pytest_cache .mypy_cache .ropeproject htmlcov .coverage
	find . -name .venv -prune -o -type d -name "__pycache__" -exec rm -rf {} +
	find . -name .venv -prune -o -type f \( -name "*.pyc" -o -name "*.pyo" -o -name ".DS_Store" \) -exec rm -f {} +
