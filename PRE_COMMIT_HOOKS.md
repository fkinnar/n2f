# Pre-commit Hooks Configuration

Ce projet utilise des hooks Git pre-commit pour assurer la qualité du code automatiquement avant chaque commit.

## 🚀 Installation

Les hooks sont déjà installés dans ce projet. Si vous clonez le projet sur une nouvelle machine, installez-les avec :

```bash
python -m pip install pre-commit
pre-commit install
```

## 🔧 Hooks Configurés

### 1. **Black** - Formatage automatique du code
- **Version** : 25.1.0
- **Configuration** : Longueur de ligne = 88 caractères
- **Action** : Formate automatiquement le code Python selon les standards Black
- **Fichiers** : Tous les fichiers `.py`

### 2. **Trailing Whitespace** - Suppression des espaces en fin de ligne
- **Action** : Supprime automatiquement les espaces et tabulations en fin de ligne
- **Fichiers** : Tous les fichiers

### 3. **End of File Fixer** - Correction des fins de fichier
- **Action** : S'assure que chaque fichier se termine par une nouvelle ligne
- **Fichiers** : Tous les fichiers

### 4. **YAML Validation** - Validation de la syntaxe YAML
- **Action** : Vérifie que les fichiers YAML sont syntaxiquement corrects
- **Fichiers** : `.yaml`, `.yml`

### 5. **Large Files Check** - Vérification des gros fichiers
- **Action** : Empêche le commit de fichiers trop volumineux
- **Fichiers** : Tous les fichiers

### 6. **Merge Conflicts Check** - Détection des conflits
- **Action** : Détecte les marqueurs de conflit Git non résolus
- **Fichiers** : Tous les fichiers

## 📝 Utilisation

### Commits automatiques
Les hooks se déclenchent automatiquement lors de chaque `git commit`. Si un hook échoue :
- Le commit est bloqué
- Les erreurs sont affichées
- Corrigez les problèmes et recommencez le commit

### Exécution manuelle
Pour exécuter les hooks manuellement sur tous les fichiers :

```bash
pre-commit run --all-files
```

Pour exécuter un hook spécifique :

```bash
pre-commit run black --all-files
pre-commit run trailing-whitespace --all-files
```

### Mise à jour des hooks
Pour mettre à jour les versions des hooks :

```bash
pre-commit autoupdate
```

## ⚠️ Dépannage

### Hooks ignorés
Si les hooks semblent ignorés, vérifiez que :
1. `pre-commit install` a été exécuté
2. Le fichier `.git/hooks/pre-commit` existe
3. Vous êtes dans le bon repository Git

### Erreurs de formatage
Si Black échoue :
1. Vérifiez la syntaxe Python
2. Exécutez `black .` manuellement pour voir les erreurs
3. Corrigez le code et recommencez

### Fichiers ignorés
Certains fichiers sont automatiquement exclus :
- `.git/`
- `.mypy_cache/`
- `__pycache__/`
- Fichiers de build et distribution

## 🔄 Workflow recommandé

1. **Développement** : Codez normalement
2. **Staging** : `git add <fichiers>`
3. **Commit** : `git commit -m "message"`
4. **Hooks automatiques** : Black formate, autres hooks vérifient
5. **Succès** : Commit créé avec code formaté
6. **Échec** : Corrigez et recommencez

## 📚 Ressources

- [Documentation pre-commit](https://pre-commit.com/)
- [Documentation Black](https://black.readthedocs.io/)
- [Configuration du projet](.pre-commit-config.yaml)

---

**Note** : Ces hooks garantissent que chaque commit respecte les standards de qualité du projet.
