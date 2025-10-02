import os
import pytest
from app.database import setup_database
from app.vector_store import setup_vector_store
from app.workflow import get_workflow

def test_workflow_invoke():
    # Skip test if no OpenAI API key is available or if it's a dummy key (e.g., in CI environment)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-dummy"):
        pytest.skip("Valid OpenAI API key not available - skipping workflow test")
    
    conn = setup_database()
    cursor = conn.cursor()
    vector_store = setup_vector_store()
    
    workflow = get_workflow(conn, cursor, vector_store)
    
    initial_state = {
        "messages": [("user", "How many customers do we have?")],
        "iterations": 0,
        "error": "",
        "results": None,
        "generation": None,
        "no_records_found": False,
        "translated_input": "",
        "database_schema": "",
    }
    
    result = workflow.invoke(initial_state)
    assert result is not None