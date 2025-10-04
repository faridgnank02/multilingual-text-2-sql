import logging
import os
import sqlite3
import json
from pathlib import Path
from typing import Optional

def get_active_database_path() -> str:
    """Get the path to the currently active database."""
    data_dir = Path(os.path.dirname(__file__)).parent / "data"
    config_file = data_dir / "database_config.json"
    databases_dir = data_dir / "databases"
    
    # Read active database from config
    active_db = "default"  # default fallback
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                active_db = config.get("active_database", "default")
        except:
            pass
    
    # Return path to active database
    db_path = databases_dir / f"{active_db}.db"
    return str(db_path)

def create_connection(db_file: str = None) -> sqlite3.Connection:
    """Create a database connection to the SQLite database."""
    if db_file is None:
        db_file = get_active_database_path()
    conn = sqlite3.connect(db_file)
    return conn

def create_tables(conn: sqlite3.Connection) -> None:
    """Create tables in the database."""
    cursor = conn.cursor()
    # Create Customers table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Customers (
            CustomerID INTEGER PRIMARY KEY,
            CustomerName TEXT,
            ContactName TEXT,
            Address TEXT,
            City TEXT,
            PostalCode TEXT,
            Country TEXT
        )
        """
    )
    # Create Orders table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Orders (
            OrderID INTEGER PRIMARY KEY,
            CustomerID INTEGER,
            OrderDate TEXT,
            FOREIGN KEY (CustomerID) REFERENCES Customers (CustomerID)
        )
        """
    )
    # Create OrderDetails table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS OrderDetails (
            OrderDetailID INTEGER PRIMARY KEY,
            OrderID INTEGER,
            ProductID INTEGER,
            Quantity INTEGER,
            FOREIGN KEY (OrderID) REFERENCES Orders (OrderID),
            FOREIGN KEY (ProductID) REFERENCES Products (ProductID)
        )
        """
    )
    # Create Products table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY,
            ProductName TEXT,
            Price REAL
        )
        """
    )
    conn.commit()

def populate_tables(conn: sqlite3.Connection) -> None:
    """Populate tables with sample data if they are empty."""
    cursor = conn.cursor()
    # Populate Customers table if empty
    cursor.execute("SELECT COUNT(*) FROM Customers")
    if cursor.fetchone()[0] == 0:
        customers = []
        for i in range(1, 51):
            customers.append(
                (
                    i,
                    f"Customer {i}",
                    f"Contact {i}",
                    f"Address {i}",
                    f"City {i % 10}",
                    f"{10000 + i}",
                    f"Country {i % 5}",
                )
            )
        cursor.executemany(
            """
            INSERT INTO Customers (CustomerID, CustomerName, ContactName, Address, City, PostalCode, Country)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            customers,
        )

    # Populate Products table if empty
    cursor.execute("SELECT COUNT(*) FROM Products")
    if cursor.fetchone()[0] == 0:
        products = []
        for i in range(1, 51):
            products.append((i, f"Product {i}", round(10 + i * 0.5, 2)))
        cursor.executemany(
            """
            INSERT INTO Products (ProductID, ProductName, Price)
            VALUES (?, ?, ?)
            """,
            products,
        )

    # Populate Orders table if empty
    cursor.execute("SELECT COUNT(*) FROM Orders")
    if cursor.fetchone()[0] == 0:
        orders = []
        from datetime import datetime, timedelta

        base_date = datetime(2023, 1, 1)
        for i in range(1, 51):
            order_date = base_date + timedelta(days=i)
            orders.append((i, i % 50 + 1, order_date.strftime("%Y-%m-%d")))
        cursor.executemany(
            """
            INSERT INTO Orders (OrderID, CustomerID, OrderDate)
            VALUES (?, ?, ?)
            """,
            orders,
        )

    # Populate OrderDetails table if empty
    cursor.execute("SELECT COUNT(*) FROM OrderDetails")
    if cursor.fetchone()[0] == 0:
        order_details = []
        for i in range(1, 51):
            order_details.append((i, i % 50 + 1, i % 50 + 1, (i % 5 + 1) * 2))
        cursor.executemany(
            """
            INSERT INTO OrderDetails (OrderDetailID, OrderID, ProductID, Quantity)
            VALUES (?, ?, ?, ?)
            """,
            order_details,
        )

    conn.commit()

def setup_database(logger: Optional[logging.Logger] = None) -> sqlite3.Connection:
    """Setup the database and return the connection."""
    if logger is None:
        logger = logging.getLogger(__name__)
    
    # Create directories if they don't exist
    data_dir = Path(os.path.dirname(__file__)).parent / "data"
    databases_dir = data_dir / "databases"
    data_dir.mkdir(exist_ok=True)
    databases_dir.mkdir(exist_ok=True)
    
    # Get active database path
    db_file = get_active_database_path()
    db_exists = os.path.exists(db_file)
    conn = create_connection(db_file)
    
    if not db_exists:
        logger.info(f"Setting up the database at {db_file}...")
        create_tables(conn)
        populate_tables(conn)
    else:
        logger.info(f"Database already exists at {db_file}. Skipping setup.")
    return conn
