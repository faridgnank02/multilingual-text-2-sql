import os
import logging
import mlflow
from dotenv import load_dotenv

from database import setup_database
from vector_store import setup_vector_store
from definitions import (
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
    # If autologging isn't available or fails, just continue
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
    # Interactive CLI loop
    # ===============================
    _logger.info("Welcome to the SQL Assistant!")
    while True:
        question = input("\nEnter your SQL question (or type 'exit' to quit): ")
        if question.lower() == "exit":
            break

        # Initial workflow state
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

        # Run workflow
        solution = app.invoke(initial_state)

        # ===============================
        # Error Handling
        # ===============================
        if solution.get("error") == "yes":
            _logger.info("\nAssistant Message:\n")
            _logger.info(solution.get("messages", [])[-1][1])
            continue

        # ===============================
        # Extract Generated SQL
        # ===============================
        gen = solution.get("generation")
        sql_query = getattr(gen, "sql_code", None) if gen is not None else None
        _logger.info("\nGenerated SQL Query:\n")
        _logger.info(sql_query or "(No SQL returned)")

        # ===============================
        # Display Results
        # ===============================
        if solution.get("no_records_found"):
            _logger.info("\nNo records found matching your query.")
        elif solution.get("results") is not None:
            _logger.info("\nQuery Results:\n")
            for row in solution["results"]:
                _logger.info(row)
        else:
            _logger.info("\nNo results returned or query did not execute successfully.")

    _logger.info("Goodbye!")


if __name__ == "__main__":
    main()
