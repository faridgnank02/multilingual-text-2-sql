from app.workflow import get_workflow
from app.database import setup_database
from app.vector_store import setup_vector_store

def test_workflow_invoke():
    conn = setup_database()
    cursor = conn.cursor()
    vector_store = setup_vector_store()
    workflow = get_workflow(conn, cursor, vector_store)
    initial_state = {
        "messages": [("user", "How many customers per country?")],
        "iterations": 0,
        "error": "",
        "results": None,
        "generation": None,
        "no_records_found": False,
        "translated_input": "",
        "database_schema": "",
    }
    result = workflow.invoke(initial_state)
    assert isinstance(result, dict)
    assert "results" in result
    conn.close()