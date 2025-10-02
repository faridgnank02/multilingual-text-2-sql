import os
import pytest
from app.vector_store import setup_vector_store

def test_vector_store_load():
    # Skip test if no OpenAI API key is available (e.g., in CI environment)
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OpenAI API key not available - skipping vector store test")
    
    vector_store = setup_vector_store()
    assert vector_store is not None
    # Vérifie qu'il y a des documents indexés
    assert hasattr(vector_store, "index")
    assert vector_store.index.ntotal > 0