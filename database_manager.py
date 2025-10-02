#!/usr/bin/env python3
"""
Database Manager - Utilitaire pour gérer les bases de données du système SQL multilingue
Permet d'importer des bases de données externes et de basculer entre elles.
"""

import os
import shutil
import sqlite3
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

# Chemins importants
DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "database.db"
CUSTOM_DB_DIR = DATA_DIR / "custom_databases"
DB_CONFIG_FILE = DATA_DIR / "database_config.json"

def ensure_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas."""
    DATA_DIR.mkdir(exist_ok=True)
    CUSTOM_DB_DIR.mkdir(exist_ok=True)

def get_database_info(db_path: str) -> Dict:
    """Récupère les informations sur une base de données."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Obtenir la liste des tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Obtenir les informations sur chaque table
        table_info = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [{"name": col[1], "type": col[2], "nullable": not col[3]} for col in cursor.fetchall()]
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            table_info[table] = {"columns": columns, "row_count": row_count}
        
        conn.close()
        return {"tables": table_info, "total_tables": len(tables)}
    except Exception as e:
        return {"error": str(e)}

def list_databases() -> Dict:
    """Liste toutes les bases de données disponibles."""
    ensure_directories()
    
    databases = {}
    
    # Base de données par défaut
    if DB_PATH.exists():
        databases["default"] = {
            "name": "Base de données par défaut (Customers/Orders/Products)",
            "path": str(DB_PATH),
            "info": get_database_info(str(DB_PATH))
        }
    
    # Bases de données personnalisées
    if CUSTOM_DB_DIR.exists():
        for db_file in CUSTOM_DB_DIR.glob("*.db"):
            db_key = db_file.stem
            databases[db_key] = {
                "name": f"Base de données personnalisée : {db_key}",
                "path": str(db_file),
                "info": get_database_info(str(db_file))
            }
    
    return databases

def import_csv_to_database(csv_path: str, db_name: str, table_name: Optional[str] = None) -> Dict:
    """Importe un fichier CSV dans une nouvelle base de données."""
    ensure_directories()
    
    if not table_name:
        table_name = Path(csv_path).stem
    
    db_path = CUSTOM_DB_DIR / f"{db_name}.db"
    
    try:
        # Créer la base de données
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)
            
            # Créer la table (tous les champs en TEXT pour simplifier)
            columns_def = ", ".join([f"{header} TEXT" for header in headers])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})")
            
            # Insérer les données
            placeholders = ", ".join(["?" for _ in headers])
            for row in csv_reader:
                # Compléter la ligne si elle a moins de colonnes que les headers
                while len(row) < len(headers):
                    row.append("")
                cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row[:len(headers)])
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"CSV importé avec succès dans la base de données '{db_name}' (table '{table_name}')",
            "db_path": str(db_path),
            "info": get_database_info(str(db_path))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def import_sql_to_database(sql_path: str, db_name: str) -> Dict:
    """Importe un fichier SQL dans une nouvelle base de données."""
    ensure_directories()
    
    db_path = CUSTOM_DB_DIR / f"{db_name}.db"
    
    try:
        conn = sqlite3.connect(str(db_path))
        
        with open(sql_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
            conn.executescript(sql_script)
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Script SQL importé avec succès dans la base de données '{db_name}'",
            "db_path": str(db_path),
            "info": get_database_info(str(db_path))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def copy_database(source_path: str, db_name: str) -> Dict:
    """Copie une base de données SQLite existante."""
    ensure_directories()
    
    db_path = CUSTOM_DB_DIR / f"{db_name}.db"
    
    try:
        shutil.copy2(source_path, str(db_path))
        return {
            "success": True,
            "message": f"Base de données copiée avec succès sous le nom '{db_name}'",
            "db_path": str(db_path),
            "info": get_database_info(str(db_path))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def set_active_database(db_key: str) -> Dict:
    """Change la base de données active utilisée par l'application."""
    ensure_directories()
    
    databases = list_databases()
    if db_key not in databases:
        return {"success": False, "error": f"Base de données '{db_key}' non trouvée"}
    
    source_path = databases[db_key]["path"]
    
    try:
        # Sauvegarder la base actuelle si elle existe
        if DB_PATH.exists():
            backup_path = DATA_DIR / "database_backup.db"
            shutil.copy2(str(DB_PATH), str(backup_path))
        
        # Copier la nouvelle base de données
        shutil.copy2(source_path, str(DB_PATH))
        
        # Sauvegarder la configuration
        config = {"active_database": db_key}
        with open(DB_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "message": f"Base de données '{databases[db_key]['name']}' activée avec succès",
            "info": get_database_info(str(DB_PATH))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_active_database() -> str:
    """Retourne la clé de la base de données active."""
    if DB_CONFIG_FILE.exists():
        try:
            with open(DB_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get("active_database", "default")
        except:
            pass
    return "default"

def main():
    """Interface en ligne de commande pour gérer les bases de données."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestionnaire de bases de données pour l'assistant SQL multilingue")
    parser.add_argument("action", choices=["list", "import-csv", "import-sql", "import-db", "set-active", "info"], 
                       help="Action à effectuer")
    parser.add_argument("--file", help="Chemin vers le fichier à importer")
    parser.add_argument("--name", help="Nom de la base de données")
    parser.add_argument("--table", help="Nom de la table (pour CSV)")
    parser.add_argument("--db-key", help="Clé de la base de données")
    
    args = parser.parse_args()
    
    if args.action == "list":
        databases = list_databases()
        active = get_active_database()
        print("\n=== Bases de données disponibles ===")
        for key, db in databases.items():
            status = " (ACTIVE)" if key == active else ""
            print(f"\n{key}{status}: {db['name']}")
            if "error" not in db["info"]:
                print(f"  Tables: {db['info']['total_tables']}")
                for table, info in db["info"]["tables"].items():
                    print(f"    - {table}: {info['row_count']} lignes")
            else:
                print(f"  Erreur: {db['info']['error']}")
    
    elif args.action == "import-csv":
        if not args.file or not args.name:
            print("Erreur: --file et --name sont requis pour import-csv")
            return
        result = import_csv_to_database(args.file, args.name, args.table)
        print(result.get("message", result.get("error", "Erreur inconnue")))
    
    elif args.action == "import-sql":
        if not args.file or not args.name:
            print("Erreur: --file et --name sont requis pour import-sql")
            return
        result = import_sql_to_database(args.file, args.name)
        print(result.get("message", result.get("error", "Erreur inconnue")))
    
    elif args.action == "import-db":
        if not args.file or not args.name:
            print("Erreur: --file et --name sont requis pour import-db")
            return
        result = copy_database(args.file, args.name)
        print(result.get("message", result.get("error", "Erreur inconnue")))
    
    elif args.action == "set-active":
        if not args.db_key:
            print("Erreur: --db-key est requis pour set-active")
            return
        result = set_active_database(args.db_key)
        print(result.get("message", result.get("error", "Erreur inconnue")))
    
    elif args.action == "info":
        if args.db_key:
            databases = list_databases()
            if args.db_key in databases:
                db = databases[args.db_key]
                print(f"\n=== Informations sur {db['name']} ===")
                if "error" not in db["info"]:
                    for table, info in db["info"]["tables"].items():
                        print(f"\nTable: {table} ({info['row_count']} lignes)")
                        for col in info["columns"]:
                            print(f"  - {col['name']}: {col['type']}")
                else:
                    print(f"Erreur: {db['info']['error']}")
            else:
                print(f"Base de données '{args.db_key}' non trouvée")
        else:
            # Afficher les infos de la base active
            active = get_active_database()
            databases = list_databases()
            if active in databases:
                db = databases[active]
                print(f"\n=== Base de données active: {db['name']} ===")
                if "error" not in db["info"]:
                    for table, info in db["info"]["tables"].items():
                        print(f"\nTable: {table} ({info['row_count']} lignes)")
                        for col in info["columns"]:
                            print(f"  - {col['name']}: {col['type']}")

if __name__ == "__main__":
    main()