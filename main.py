import os
import sys
import logging
import mlflow
from dotenv import load_dotenv

# Add current directory and app directory to Python path for MLflow model loading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.database import setup_database
from app.vector_store import setup_vector_store
from app.definitions import (
    EXPERIMENT_NAME,
    MODEL_ALIAS,
    REGISTERED_MODEL_NAME,
    REMOTE_SERVER_URI,
)

# ===============================
# Configure MLflow
# ===============================
mlflow.set_tracking_uri(REMOTE_SERVER_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

# Enable LangChain autologging for tracing
try:
    mlflow.langchain.autolog()
except Exception:  
    pass

# ===============================
# Logger Setup
# ===============================
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
_logger.addHandler(handler)


def main():
    """
    Main entry point for the multilingual text-to-SQL assistant.
    Loads the workflow from MLflow, initializes database and vector store,
    and runs an interactive CLI loop for user queries.
    """
    # Load environment variables from .env
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

    # ===============================
    # Setup database and vector store
    # ===============================
    conn = setup_database(_logger)
    cursor = conn.cursor()
    vector_store = setup_vector_store(_logger)

    if conn is None or cursor is None or vector_store is None:
        _logger.error("Database connection, cursor, or vector store is None.")
        return

    # ===============================
    # Load model from MLflow registry
    # ===============================
    model_uri = f"models:/{REGISTERED_MODEL_NAME}@{MODEL_ALIAS}"
    _logger.info("Loading model from %s", model_uri)
    model = mlflow.pyfunc.load_model(model_uri)

    # Model input must be a list of dictionaries as expected by SQLGenerator
    model_input = [{"conn": conn, "cursor": cursor, "vector_store": vector_store}]
    
    # model.predict returns the compiled LangGraph workflow
    app = model.predict(model_input)
    _logger.info("Model loaded and workflow compiled successfully.")

    # Optionally save a diagram of the graph
    try:
        app.get_graph().draw_mermaid_png(output_file_path="sql_agent_with_safety_checks.png")
        _logger.info("Workflow diagram saved to sql_agent_with_safety_checks.png")
    except Exception as e:
        _logger.warning("Could not save workflow diagram: %s", str(e))

    # ===============================
    # Interactive CLI loop with MLflow tracking
    # ===============================
    _logger.info("Welcome to the SQL Assistant!")
    run_idx = 1
    while True:
        question = input("\nEnter your SQL question (or type 'exit' to quit): ")
        if question.lower() == "exit":
            break

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

        # === MLflow tracking for each query ===
        with mlflow.start_run(run_name=f"sql_generation_run_{run_idx}"):
            mlflow.log_param("question", question)

            # Optionally log database schema for traceability
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                mlflow.log_param("database_tables", str([t[0] for t in tables]))
            except Exception:
                pass

            import time
            start_time = time.time()
            solution = app.invoke(initial_state)
            duration = time.time() - start_time
            mlflow.log_metric("duration_seconds", duration)

            if solution.get("error") == "yes":
                mlflow.log_param("error", solution.get("messages", [])[-1][1])
                _logger.info("\nAssistant Message:\n")
                _logger.info(solution.get("messages", [])[-1][1])
                run_idx += 1
                continue

            gen = solution.get("generation")
            sql_query = getattr(gen, "sql_code", None) if gen is not None else None
            mlflow.log_param("sql_query", sql_query or "(No SQL returned)")

            # Log translated input if available
            translated_input = solution.get("translated_input", "")
            if translated_input:
                mlflow.log_param("translated_input", translated_input)

            if solution.get("no_records_found"):
                mlflow.log_param("no_records_found", True)
                _logger.info("\nNo records found matching your query.")
            elif solution.get("results") is not None:
                # Save results as artifact
                import tempfile, json
                with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
                    json.dump(solution["results"], f)
                    mlflow.log_artifact(f.name, artifact_path="results")
                _logger.info("\nQuery Results:\n")
                for row in solution["results"]:
                    _logger.info(row)
            else:
                _logger.info("\nNo results returned or query did not execute successfully.")

        run_idx += 1

    _logger.info("Goodbye!")


if __name__ == "__main__":
    main()
