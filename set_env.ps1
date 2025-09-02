# Script PowerShell pour configurer l'environnement Python pour le projet N2F

# Configuration du PYTHONPATH
$env:PYTHONPATH = "src;D:\Users\kinnar\sourceepos\common\Python\Packages"

# Affichage de la configuration
Write-Host "PYTHONPATH configuré:" -ForegroundColor Green
Write-Host $env:PYTHONPATH -ForegroundColor Yellow
Write-Host ""

Write-Host "Vous pouvez maintenant exécuter:" -ForegroundColor Green
Write-Host "  python src/sync-agresso-n2f.py --help" -ForegroundColor Cyan
Write-Host "  python -m pytest tests/ -v" -ForegroundColor Cyan
Write-Host ""

Write-Host "Ou lancer une nouvelle session avec:" -ForegroundColor Green
Write-Host "  .\set_env.ps1" -ForegroundColor Cyan
