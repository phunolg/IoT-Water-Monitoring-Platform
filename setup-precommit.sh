#!/bin/bash

echo "Setting up pre-commit hooks for Smart Water Monitoring System..."
echo "Installing pre-commit..."
pip install pre-commit
echo "Installing pre-commit hooks..."
pre-commit install

echo "Testing pre-commit on all files..."
pre-commit run --all-files

echo "Pre-commit setup complete!"
echo ""
echo "Usage:"
echo "  • pre-commit will now run automatically on every git commit"
echo "  • To run manually: pre-commit run --all-files"
echo "  • To skip hooks: git commit --no-verify"
echo ""
echo "Hooks configured:"
echo "  • Black (code formatting)"
echo "  • isort (import sorting)"
echo "  • flake8 (linting)"
echo "  • trailing-whitespace removal"
echo "  • end-of-file-fixer"
echo "  • Django checks"
