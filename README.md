# 🔄 N2F Synchronization Tool

Outil de synchronisation entre Agresso et N2F pour la gestion des utilisateurs,
projets, plaques et sous-posts.

## 📋 Vue d'ensemble

Ce projet permet de synchroniser automatiquement les données entre le système
Agresso et l'API N2F. Il gère la création, mise à jour et suppression d'entités
de manière cohérente et traçable.

### 🎯 Fonctionnalités principales

- ✅ **Synchronisation multi-scopes** : Users, Projects, Plates, Subposts

- ✅ **Gestion d'erreur robuste** : Exceptions personnalisées avec contexte riche

- ✅ **Architecture modulaire** : Classes abstraites pour extensibilité

- ✅ **Logging détaillé** : Export des logs d'API avec métriques

- ✅ **Configuration flexible** : Support dev/prod avec fichiers YAML

- ✅ **Cache intelligent** : Optimisation des performances API

## 🚀 Installation et configuration

### Prérequis

- Python 3.13+

- Accès aux bases de données Agresso

- Credentials N2F API

### Installation

```bash

## Cloner le repository

git clone <repository-url>
cd n2f

## Créer un environnement virtuel

python -m venv env
source env/bin/activate  # Linux/Mac

## ou

env\Scripts\activate     # Windows

## Installer les dépendances

pip install -r requirements.txt




```
