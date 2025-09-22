from app.vector_store import setup_vector_store

def test_vector_store_load():
    vector_store = setup_vector_store()
    assert vector_store is not None
    # Vérifie qu'il y a des documents indexés
    assert hasattr(vector_store, "index")
    assert vector_store.index.ntotal > 0