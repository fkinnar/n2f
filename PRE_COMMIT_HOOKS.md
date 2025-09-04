# Pre-commit Hooks Configuration

Ce projet utilise des hooks Git pre-commit pour assurer la qualitÃ© du code
automatiquement avant chaque commit.

## ðŸš€ Installation

### Installation des dÃ©pendances de dÃ©veloppement

Si vous clonez le projet sur une nouvelle machine, installez d'abord toutes les
dÃ©pendances de dÃ©veloppement :

```bash
# Via pyproject.toml
python -m pip install -e ".[dev]"
```

### Installation des hooks pre-commit

Une fois les dÃ©pendances installÃ©es, installez les hooks :

```bash
pre-commit install
```

## ðŸ”§ Hooks ConfigurÃ©s

### 1. **Black** - Formatage automatique du code

- **Version** : 25.1.0
- **Configuration** : Longueur de ligne = 88 caractÃ¨res
- **Action** : Formate automatiquement le code Python selon les standards Black
- **Fichiers** : Tous les fichiers `.py`

### 2. **Flake8** - VÃ©rification de la qualitÃ© du code

- **Version** : 7.1.1
- **Configuration** : Fichier `.flake8` avec rÃ¨gles personnalisÃ©es
- **Action** : VÃ©rifie le style, les erreurs et la complexitÃ© du code Python
- **Fichiers** : Tous les fichiers `.py`

### 3. **Trailing Whitespace** - Suppression des espaces en fin de ligne

- **Action** : Supprime automatiquement les espaces et tabulations en fin de ligne
- **Fichiers** : Tous les fichiers

### 3. **End of File Fixer** - Correction des fins de fichier

- **Action** : S'assure que chaque fichier se termine par une nouvelle ligne
- **Fichiers** : Tous les fichiers

### 4. **YAML Validation** - Validation de la syntaxe YAML

- **Action** : VÃ©rifie que les fichiers YAML sont syntaxiquement corrects
- **Fichiers** : `.yaml`, `.yml`

### 5. **Large Files Check** - VÃ©rification des gros fichiers

- **Action** : EmpÃªche le commit de fichiers trop volumineux
- **Fichiers** : Tous les fichiers

### 6. **Merge Conflicts Check** - DÃ©tection des conflits

- **Action** : DÃ©tecte les marqueurs de conflit Git non rÃ©solus
- **Fichiers** : Tous les fichiers

## ðŸ“ Utilisation

### Commits automatiques

Les hooks se dÃ©clenchent automatiquement lors de chaque `git commit`. Si un hook
Ã©choue :

- Le commit est bloquÃ©
- Les erreurs sont affichÃ©es
- Corrigez les problÃ¨mes et recommencez le commit

### ExÃ©cution manuelle

Pour exÃ©cuter les hooks manuellement sur tous les fichiers :

```bash
pre-commit run --all-files
```

Pour exÃ©cuter un hook spÃ©cifique :

```bash
pre-commit run black --all-files
pre-commit run flake8 --all-files
pre-commit run trailing-whitespace --all-files
```

### Mise Ã  jour des hooks

Pour mettre Ã  jour les versions des hooks :

```bash
pre-commit autoupdate
```

## âš ï¸ DÃ©pannage

### Hooks ignorÃ©s

Si les hooks semblent ignorÃ©s, vÃ©rifiez que :

1. `pre-commit install` a été exécuté
1. Le fichier `.git/hooks/pre-commit` existe
1. Vous êtes dans le bon repository Git

### Erreurs de formatage

Si Black Ã©choue :

1. Vérifiez la syntaxe Python
1. Exécutez `black .` manuellement pour voir les erreurs
1. Corrigez le code et recommencez

### Fichiers ignorÃ©s

Certains fichiers sont automatiquement exclus :

- `.git/`
- `.mypy_cache/`
- `__pycache__/`
- Fichiers de build et distribution

## ðŸ”„ Workflow recommandÃ©

1. **Développement** : Codez normalement
1. **Staging** : `git add <fichiers>`
1. **Commit** : `git commit -m "message"`
1. **Hooks automatiques** : Black formate, autres hooks vérifient
1. **Succès** : Commit créé avec code formaté
1. **Échec** : Corrigez et recommencez

## ðŸ“š Ressources

- [Documentation pre-commit](https://pre-commit.com/)
- [Documentation Black](https://black.readthedocs.io/)
- [Configuration du projet](.pre-commit-config.yaml)

______________________________________________________________________

**Note** : Ces hooks garantissent que chaque commit respecte les standards de qualitÃ©
du projet.
