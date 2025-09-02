@echo off
REM Script pour configurer l'environnement Python pour le projet N2F

REM Configuration du PYTHONPATH
set PYTHONPATH=src;D:\Users\kinnar\source\repos\common\Python\Packages

REM Affichage de la configuration
echo PYTHONPATH configure:
echo %PYTHONPATH%
echo.
echo Vous pouvez maintenant executer:
  echo   python src/sync-agresso-n2f.py --help
  echo   python -m pytest tests/ -v
echo.
echo Ou lancer une nouvelle session PowerShell avec:
  echo   $env:PYTHONPATH="src;D:\Users\kinnar\source\repos\common\Python\Packages"
