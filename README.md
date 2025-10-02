# Multilingual Text to SQL

Ce projet fournit une interface web pour convertir des questions en langage naturel (dans plusieurs langues) en requêtes SQL et les exécuter sur des bases de données personnalisables.

## 🚀 Fonctionnalités

- **Multilinguisme** : Questions en français, anglais, et autres langues
- **Bases de données flexibles** : Système par défaut + import de vos propres bases
- **Interface améliorée** : Explications des requêtes repositionnées et clarifiées  
- **Sécurité** : Vérifications multiples contre l'injection SQL
- **Recherche sémantique** : Store vectoriel FAISS pour améliorer la génération SQL
- **MLflow** : Tracking et versioning des modèles
- **Interface web Flask** : Interface simple et intuitive

## 🆕 Nouveautés

- **Gestionnaire de bases de données** : Import facile de CSV, SQL, ou bases SQLite
- **Exemples inclus** : Bibliothèque, École, Employés
- **Interface restructurée** : "Generated answer" → "Query Explanation" en bas de page
- **Upload simplifié** : Fonctionnalité d'upload défaillante supprimée, remplacée par un système robuste

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/faridgnank02/multilingual-text-2-sql.git
cd multilingual-text-2-sql
```

### 2. Create and activate a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and fill in your API keys and configuration.

```bash
cp .env.example .env
```

### 5. Démarrage rapide

#### Option A : Utiliser la base de données par défaut
```bash
python3 app.py
```

#### Option B : Importer et utiliser vos propres données
```bash
# Import d'un exemple (bibliothèque)
python3 database_manager.py import-sql --file examples/bibliotheque.sql --name bibliotheque

# Activation de la nouvelle base
python3 database_manager.py set-active --db-key bibliotheque

# Lancement de l'application
python3 app.py
```

L'application web sera disponible sur [http://localhost:5001](http://localhost:5001).

## 📊 Utilisation avec vos propres bases de données

### Import de données

```bash
# CSV
python3 database_manager.py import-csv --file votre_fichier.csv --name ma_base --table ma_table

# Script SQL
python3 database_manager.py import-sql --file votre_script.sql --name ma_base

# Base SQLite existante
python3 database_manager.py import-db --file votre_base.db --name ma_base
```

### Gestion des bases

```bash
# Lister toutes les bases disponibles
python3 database_manager.py list

# Changer de base active
python3 database_manager.py set-active --db-key nom_de_votre_base

# Voir les détails d'une base
python3 database_manager.py info --db-key nom_de_votre_base
```

## 🧪 Exemples de test

Le projet inclut 3 bases de données d'exemple :

### 📚 Bibliothèque (`examples/bibliotheque.sql`)
```bash
python3 database_manager.py import-sql --file examples/bibliotheque.sql --name bibliotheque
python3 database_manager.py set-active --db-key bibliotheque
```
**Questions à tester :**
- "Combien de livres sont actuellement empruntés ?"
- "Quels auteurs français avons-nous ?"
- "Qui a emprunté des livres de Camus ?"

### 🎓 École (`examples/ecole.sql`)
```bash
python3 database_manager.py import-sql --file examples/ecole.sql --name ecole
python3 database_manager.py set-active --db-key ecole
```
**Questions à tester :**
- "Quelle est la moyenne de l'étudiant Alice Martin ?"
- "Combien d'étudiants sont inscrits en informatique ?"
- "Quels cours enseigne le professeur Dupont ?"

### 👥 Employés (`examples/employes.csv`)
```bash
python3 database_manager.py import-csv --file examples/employes.csv --name employes --table employes
python3 database_manager.py set-active --db-key employes
```
**Questions à tester :**
- "Quel est le salaire moyen par département ?"
- "Combien d'employés travaillent à Paris ?"
- "Qui sont les employés les mieux payés ?"

## 🚀 Démonstration automatique

Pour importer tous les exemples et voir les instructions :
```bash
python3 demo.py
```

## Main Files

- `app.py` : Main Flask application
- `database.py` : Database setup and population
- `vector_store.py` : Vector store setup
- `definitions.py` : Configuration constants
- `requirements.txt` : Python dependencies
- `templates/index.html` : Web interface

## Notes

- The database and vector store are generated automatically and should not be committed to Git.
- Do not commit your `.env` file containing secrets.