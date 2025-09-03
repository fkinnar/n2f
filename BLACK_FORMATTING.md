# Formatage du code avec Black

Ce projet utilise [Black](https://black.readthedocs.io/) pour maintenir un formatage de code Python cohérent et automatique.

## Qu'est-ce que Black ?

Black est un formateur de code Python qui applique automatiquement un style de code cohérent. Il suit les recommandations PEP 8 et d'autres conventions Python, en se concentrant sur la lisibilité et la cohérence.

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

### Vérification du formatage

Pour vérifier que tous les fichiers sont correctement formatés sans les modifier :

```bash
black --check src/ tests/ python/ scripts/
```

### Script de formatage

Le projet inclut un script de formatage personnalisé :

```bash
# Formater le code
python scripts/format_code.py

# Vérifier le formatage
python scripts/format_code.py --check
```

## Intégration avec pre-commit

Le projet est configuré avec pre-commit pour automatiser le formatage lors des commits. Pour l'installer :

```bash
# Installer pre-commit
pip install pre-commit

# Installer les hooks
pre-commit install
```

Après l'installation, Black s'exécutera automatiquement sur tous les fichiers Python modifiés lors de chaque commit.

## Règles de formatage

Black applique automatiquement les règles suivantes :

- **Longueur de ligne** : 88 caractères (conforme à PEP 8)
- **Guillemets** : Double guillemets pour les chaînes
- **Espaces** : Suppression des espaces en fin de ligne
- **Virgules** : Ajout automatique des virgules finales
- **Imports** : Tri et formatage automatique des imports
- **Indentation** : 4 espaces (pas de tabs)

## Avantages

- **Cohérence** : Tous les développeurs utilisent le même style
- **Lisibilité** : Code plus facile à lire et maintenir
- **Automatisation** : Pas besoin de penser au formatage
- **Intégration** : Fonctionne avec la plupart des éditeurs et IDEs
- **Standards** : Respecte les conventions Python officielles

## Résolution des conflits

Si Black modifie un fichier et que vous avez des modifications non commitées, vous pouvez :

1. **Accepter les changements de Black** (recommandé)
2. **Reformater manuellement** avec `black <fichier>`
3. **Utiliser l'option `--skip-string-normalization`** si nécessaire

## Support des éditeurs

### VS Code
Installez l'extension Python et configurez Black comme formateur par défaut.

### PyCharm
Configurez Black comme formateur externe dans les paramètres.

### Vim/Neovim
Utilisez des plugins comme `black.vim` ou `ale`.

## Maintenance

Pour maintenir le formatage du projet :

1. **Avant chaque commit** : Black s'exécute automatiquement
2. **Régulièrement** : Exécutez `black --check` pour vérifier
3. **CI/CD** : Intégrez Black dans votre pipeline de build

## Ressources

- [Documentation officielle de Black](https://black.readthedocs.io/)
- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Configuration Black dans pyproject.toml](https://black.readthedocs.io/en/stable/usage_and_configuration/the_basics.html#configuration-via-a-file)
