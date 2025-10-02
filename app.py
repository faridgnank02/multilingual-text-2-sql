import os
import sys
import mlflow
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
import sqlite3
import csv
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from pathlib import Path
import tempfile
import shutil

from app.database import setup_database
from app.vector_store import setup_vector_store
from app.definitions import (
    EXPERIMENT_NAME,
    MODEL_ALIAS,
    REGISTERED_MODEL_NAME,
    REMOTE_SERVER_URI,
)
from database_manager import (
    get_active_database, 
    list_databases, 
    import_csv_to_database, 
    import_sql_to_database, 
    copy_database, 
    set_active_database,
    ensure_directories
)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')

# Configuration pour l'upload de fichiers
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'csv', 'sql', 'db', 'sqlite', 'sqlite3'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max

# Chargement du modèle et des ressources au démarrage
conn = setup_database()
cursor = conn.cursor()
vector_store = setup_vector_store()
model_uri = f"models:/{REGISTERED_MODEL_NAME}@{MODEL_ALIAS}"
model = mlflow.pyfunc.load_model(model_uri)
model_input = [{"conn": conn, "cursor": cursor, "vector_store": vector_store}]
app_workflow = model.predict(model_input)

def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Détermine le type de fichier basé sur l'extension."""
    if not filename:
        return None
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'csv':
        return 'csv'
    elif ext == 'sql':
        return 'sql'
    elif ext in ['db', 'sqlite', 'sqlite3']:
        return 'sqlite'
    return None

def process_uploaded_file(file, db_name, table_name=None):
    """Traite le fichier uploadé et l'importe dans le système."""
    ensure_directories()
    
    if not file or not allowed_file(file.filename):
        return {"success": False, "error": "Type de fichier non autorisé"}
    
    # Créer un dossier temporaire
    temp_dir = Path(UPLOAD_FOLDER)
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Sauvegarder le fichier temporairement
        filename = secure_filename(file.filename)
        temp_file_path = temp_dir / filename
        file.save(str(temp_file_path))
        
        # Vérifier la taille du fichier
        if temp_file_path.stat().st_size > MAX_FILE_SIZE:
            temp_file_path.unlink()
            return {"success": False, "error": "Fichier trop volumineux (max 50MB)"}
        
        # Traiter selon le type de fichier
        file_type = get_file_type(filename)
        
        if file_type == 'csv':
            result = import_csv_to_database(str(temp_file_path), db_name, table_name)
        elif file_type == 'sql':
            result = import_sql_to_database(str(temp_file_path), db_name)
        elif file_type == 'sqlite':
            result = copy_database(str(temp_file_path), db_name)
        else:
            return {"success": False, "error": "Type de fichier non reconnu"}
        
        # Nettoyer le fichier temporaire
        temp_file_path.unlink()
        
        return result
        
    except Exception as e:
        # Nettoyer en cas d'erreur
        if temp_file_path.exists():
            temp_file_path.unlink()
        return {"success": False, "error": f"Erreur lors du traitement: {str(e)}"}

@app.route("/", methods=["GET", "POST"])
def index():
    sql_query = None
    results = None
    error_msg = None
    generated_answer = None
    
    # Récupérer les informations de la base de données active
    active_db_key = get_active_database()
    databases = list_databases()
    active_db_info = databases.get(active_db_key, {})
    active_db_name = active_db_info.get("name", "Base de données inconnue")

    conn = setup_database()
    cursor = conn.cursor()
    vector_store = setup_vector_store()
    model_input = [{"conn": conn, "cursor": cursor, "vector_store": vector_store}]
    app_workflow = model.predict(model_input)

    if request.method == "POST":
        action = request.form.get("action", "")
        
        # Gestion de l'upload de fichier
        if action == "upload":
            if 'db_file' not in request.files:
                error_msg = "Aucun fichier sélectionné"
            else:
                file = request.files['db_file']
                db_name = request.form.get('db_name', '').strip()
                table_name = request.form.get('table_name', '').strip()
                auto_activate = request.form.get('auto_activate') == 'on'
                
                if not db_name:
                    error_msg = "Nom de base de données requis"
                elif file.filename == '':
                    error_msg = "Aucun fichier sélectionné"
                else:
                    # Traiter le fichier
                    result = process_uploaded_file(file, db_name, table_name if table_name else None)
                    
                    if result.get("success"):
                        success_msg = result.get("message", "Fichier importé avec succès")
                        
                        # Activer automatiquement la nouvelle base si demandé
                        if auto_activate:
                            activate_result = set_active_database(db_name)
                            if activate_result.get("success"):
                                success_msg += f" Base de données '{db_name}' activée."
                                # Rediriger pour rafraîchir l'affichage de la base active
                                return redirect(url_for('index'))
                            else:
                                success_msg += " (Erreur d'activation automatique)"
                        
                        generated_answer = success_msg
                    else:
                        error_msg = result.get("error", "Erreur lors de l'import")
        
        # Gestion de la question utilisateur
        elif action == "question" or not action:  # action vide pour compatibilité
            question = request.form.get("question", "")
            if question:
                initial_state = {
                    "messages": [("user", question)],
                    "iterations": 0,
                    "error": "",
                    "results": None,
                    "generation": None,
                    "no_records_found": False,
                    "translated_input": "",
                    "database_schema": "",
                }
                try:
                    solution = app_workflow.invoke(initial_state)
                    gen = solution.get("generation")
                    sql_query = getattr(gen, "sql_code", None) if gen is not None else None
                    generated_answer = getattr(gen, "description", None) if gen is not None else None
                    if solution.get("error") == "yes":
                        error_msg = solution.get("messages", [])[-1][1]
                    elif solution.get("no_records_found"):
                        results = "Aucun résultat trouvé."
                    elif solution.get("results") is not None:
                        results = solution["results"]
                except Exception as e:
                    error_msg = str(e)
        cursor.close()
        conn.close()
    return render_template("index.html", 
                         sql_query=sql_query, 
                         results=results, 
                         error_msg=error_msg, 
                         generated_answer=generated_answer,
                         active_db_name=active_db_name,
                         active_db_key=active_db_key)


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Par exemple, utilise le port 5001