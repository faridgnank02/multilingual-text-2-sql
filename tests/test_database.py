from src.database import setup_database

def test_database_connection():
    conn = setup_database()
    assert conn is not None
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    # Vérifie qu'au moins une table existe (flexible selon la base active)
    assert len(tables) > 0, "Database should contain at least one table"
    
    # Test qu'on peut faire une requête basique sur la première table
    first_table = tables[0]
    cursor.execute(f"SELECT COUNT(*) FROM {first_table}")
    count = cursor.fetchone()[0]
    assert count >= 0, f"Should be able to query table {first_table}"
    
    conn.close()