# Formatage du code avec Black

Ce projet utilise [Black](https://black.readthedocs.io/) pour maintenir un formatage de code Python cohÃ©rent et automatique.

## Qu'est-ce que Black ?

Black est un formateur de code Python qui applique automatiquement un style de code cohÃ©rent. Il suit les recommandations PEP 8 et d'autres conventions Python, en se concentrant sur la lisibilitÃ© et la cohÃ©rence.

## Configuration

La configuration de Black se trouve dans le fichier `pyproject.toml` :

```toml
[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311', 'py312', 'py313']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

## Utilisation

### Formatage manuel

Pour formater tous les fichiers Python du projet :

```bash
# Activer l'environnement virtuel
.\env\Scripts\activate

# Formater avec Black
black src/ tests/ python/ scripts/
```

### VÃ©rification du formatage

Pour vÃ©rifier que tous les fichiers sont correctement formatÃ©s sans les modifier :

```bash
black --check src/ tests/ python/ scripts/
```

### Script de formatage

Le projet inclut un script de formatage personnalisÃ© :

```bash
# Formater le code
python scripts/format_code.py

# VÃ©rifier le formatage
python scripts/format_code.py --check
```

## IntÃ©gration avec pre-commit

Le projet est configurÃ© avec pre-commit pour automatiser le formatage lors des commits. Pour l'installer :

```bash
# Installer pre-commit
pip install pre-commit

# Installer les hooks
pre-commit install
```

AprÃ¨s l'installation, Black s'exÃ©cutera automatiquement sur tous les fichiers Python modifiÃ©s lors de chaque commit.

## RÃ¨gles de formatage

Black applique automatiquement les rÃ¨gles suivantes :

- **Longueur de ligne** : 88 caractÃ¨res (conforme Ã  PEP 8)
- **Guillemets** : Double guillemets pour les chaÃ®nes
- **Espaces** : Suppression des espaces en fin de ligne
- **Virgules** : Ajout automatique des virgules finales
- **Imports** : Tri et formatage automatique des imports
- **Indentation** : 4 espaces (pas de tabs)

## Avantages

- **CohÃ©rence** : Tous les dÃ©veloppeurs utilisent le mÃªme style
- **LisibilitÃ©** : Code plus facile Ã  lire et maintenir
- **Automatisation** : Pas besoin de penser au formatage
- **IntÃ©gration** : Fonctionne avec la plupart des Ã©diteurs et IDEs
- **Standards** : Respecte les conventions Python officielles

## RÃ©solution des conflits

Si Black modifie un fichier et que vous avez des modifications non commitÃ©es, vous pouvez :

1. **Accepter les changements de Black** (recommandÃ©)
2. **Reformater manuellement** avec `black <fichier>`
3. **Utiliser l'option `--skip-string-normalization`** si nÃ©cessaire

## Support des Ã©diteurs

### VS Code

Installez l'extension Python et configurez Black comme formateur par dÃ©faut.

### PyCharm

Configurez Black comme formateur externe dans les paramÃ¨tres.

### Vim/Neovim

Utilisez des plugins comme `black.vim` ou `ale`.

## Maintenance

Pour maintenir le formatage du projet :

1. **Avant chaque commit** : Black s'exÃ©cute automatiquement
2. **RÃ©guliÃ¨rement** : ExÃ©cutez `black --check` pour vÃ©rifier
3. **CI/CD** : IntÃ©grez Black dans votre pipeline de build

## Ressources

- [Documentation officielle de Black](https://black.readthedocs.io/)
- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Configuration Black dans pyproject.toml](https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#configuration-via-a-file)
