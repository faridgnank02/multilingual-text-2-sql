from app.database import setup_database

def test_database_connection():
    conn = setup_database()
    assert conn is not None
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    # Vérifie que les tables principales existent
    for table in ["Customers", "Orders", "OrderDetails", "Products"]:
        assert table in tables
    conn.close()