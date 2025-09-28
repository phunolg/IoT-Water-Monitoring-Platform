Write-Host "Setting up pre-commit hooks for Smart Water Monitoring System..." -ForegroundColor Green

Write-Host "Installing pre-commit..." -ForegroundColor Yellow
pip install pre-commit

Write-Host "Installing pre-commit hooks..." -ForegroundColor Yellow
pre-commit install

Write-Host "Testing pre-commit on all files..." -ForegroundColor Yellow
pre-commit run --all-files

Write-Host "Pre-commit setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  • pre-commit will now run automatically on every git commit"
Write-Host "  • To run manually: pre-commit run --all-files"
Write-Host "  • To skip hooks: git commit --no-verify"
Write-Host ""
Write-Host "Hooks configured:" -ForegroundColor Cyan
Write-Host "  • Black (code formatting)"
Write-Host "  • isort (import sorting)"
Write-Host "  • flake8 (linting)"
Write-Host "  • trailing-whitespace removal"
Write-Host "  • end-of-file-fixer"
Write-Host "  • Django checks"
