#!/usr/bin/env python3
"""
Database Manager - Utility to manage databases for the multilingual SQL system
Allows importing external databases and switching between them.
"""

import os
import shutil
import sqlite3
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

# Important paths
DATA_DIR = Path("data")
DATABASES_DIR = DATA_DIR / "databases"
DB_CONFIG_FILE = DATA_DIR / "database_config.json"

def ensure_directories():
    """Create necessary directories if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    DATABASES_DIR.mkdir(exist_ok=True)

def get_database_info(db_path: str) -> Dict:
    """Get information about a database."""
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
    """List all available databases."""
    ensure_directories()
    
    databases = {}
    
    # All databases in the databases directory
    if DATABASES_DIR.exists():
        for db_file in DATABASES_DIR.glob("*.db"):
            db_key = db_file.stem
            if db_key == "default":
                databases[db_key] = {
                    "name": "Default database (Customers/Orders/Products)",
                    "path": str(db_file),
                    "info": get_database_info(str(db_file))
                }
            else:
                databases[db_key] = {
                    "name": f"Custom database: {db_key}",
                    "path": str(db_file),
                    "info": get_database_info(str(db_file))
                }
    
    return databases

def import_csv_to_database(csv_path: str, db_name: str, table_name: Optional[str] = None) -> Dict:
    """Import a CSV file into a new database."""
    ensure_directories()
    
    if not table_name:
        table_name = Path(csv_path).stem
    
    db_path = DATABASES_DIR / f"{db_name}.db"
    
    try:
        # Create the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)
            
            # Create table (all fields as TEXT for simplicity)
            columns_def = ", ".join([f"{header} TEXT" for header in headers])
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_def})")
            
            # Insert the data
            placeholders = ", ".join(["?" for _ in headers])
            for row in csv_reader:
                # Complete the row if it has fewer columns than headers
                while len(row) < len(headers):
                    row.append("")
                cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", row[:len(headers)])
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"CSV imported successfully into database '{db_name}' (table '{table_name}')",
            "db_path": str(db_path),
            "info": get_database_info(str(db_path))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def import_sql_to_database(sql_path: str, db_name: str) -> Dict:
    """Import a SQL file into a new database."""
    ensure_directories()
    
    db_path = DATABASES_DIR / f"{db_name}.db"
    
    try:
        conn = sqlite3.connect(str(db_path))
        
        with open(sql_path, 'r', encoding='utf-8') as file:
            sql_script = file.read()
            conn.executescript(sql_script)
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"SQL script imported successfully into database '{db_name}'",
            "db_path": str(db_path),
            "info": get_database_info(str(db_path))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def copy_database(source_path: str, db_name: str) -> Dict:
    """Copy an existing SQLite database."""
    ensure_directories()
    
    db_path = DATABASES_DIR / f"{db_name}.db"
    
    try:
        shutil.copy2(source_path, str(db_path))
        return {
            "success": True,
            "message": f"Database copied successfully as '{db_name}'",
            "db_path": str(db_path),
            "info": get_database_info(str(db_path))
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def set_active_database(db_key: str) -> Dict:
    """Change the active database used by the application."""
    ensure_directories()
    
    databases = list_databases()
    if db_key not in databases:
        return {"success": False, "error": f"Database '{db_key}' not found"}
    
    try:
        # Save configuration - just store which database is active
        config = {"active_database": db_key}
        with open(DB_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "success": True,
            "message": f"Database '{databases[db_key]['name']}' activated successfully",
            "info": databases[db_key]["info"]
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