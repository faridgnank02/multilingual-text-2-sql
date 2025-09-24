import os
import sys
import mlflow
from flask import Flask, request, jsonify, render_template
import sqlite3
import csv
from dotenv import load_dotenv

from app.database import setup_database
from app.vector_store import setup_vector_store
from app.definitions import (
    EXPERIMENT_NAME,
    MODEL_ALIAS,
    REGISTERED_MODEL_NAME,
    REMOTE_SERVER_URI,
)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

app = Flask(__name__)

# Chargement du modèle et des ressources au démarrage
conn = setup_database()
cursor = conn.cursor()
vector_store = setup_vector_store()
model_uri = f"models:/{REGISTERED_MODEL_NAME}@{MODEL_ALIAS}"
model = mlflow.pyfunc.load_model(model_uri)
model_input = [{"conn": conn, "cursor": cursor, "vector_store": vector_store}]
app_workflow = model.predict(model_input)

@app.route("/", methods=["GET", "POST"])
def index():
    sql_query = None
    results = None
    error_msg = None
    generated_answer = None

    conn = setup_database()
    cursor = conn.cursor()
    vector_store = setup_vector_store()
    model_input = [{"conn": conn, "cursor": cursor, "vector_store": vector_store}]
    app_workflow = model.predict(model_input)

    if request.method == "POST":
        # Gestion de l'upload de table
        if "table_file" in request.files:
            file = request.files["table_file"]
            if file.filename.endswith(".csv"):
                try:
                    table_name = file.filename.rsplit(".", 1)[0]
                    reader = csv.reader(file.stream.read().decode("utf-8").splitlines())
                    headers = next(reader)
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([h+' TEXT' for h in headers])})")
                    for row in reader:
                        cursor.execute(f"INSERT INTO {table_name} VALUES ({', '.join(['?' for _ in row])})", row)
                    conn.commit()
                    generated_answer = f"Table '{table_name}' importée avec succès."
                except Exception as e:
                    error_msg = f"Erreur import CSV : {str(e)}"
            elif file.filename.endswith(".sql"):
                try:
                    sql_script = file.stream.read().decode("utf-8")
                    cursor.executescript(sql_script)
                    conn.commit()
                    generated_answer = f"Script SQL importé avec succès."
                except Exception as e:
                    error_msg = f"Erreur import SQL : {str(e)}"
        # Gestion de la question utilisateur
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
    return render_template("index.html", sql_query=sql_query, results=results, error_msg=error_msg, generated_answer=generated_answer)


if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Par exemple, utilise le port 5001