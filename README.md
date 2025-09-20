# Multilingual Text to SQL

This project provides a web interface to convert natural language questions (in multiple languages) into SQL queries and execute them on a sample database.

## Features

- Multilingual question-to-SQL conversion
- Sample SQLite database with Customers, Orders, Products, and OrderDetails tables
- Vector store for semantic search
- MLflow model integration
- Flask web interface

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/faridgnank02/multilingual-text-2-sql.git
cd multilingual-text-2-sql
```

### 2. Create and activate a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and fill in your API keys and configuration.

```bash
cp .env.example .env
```

### 5. Run the application

```bash
python app.py
```

The web app will be available at [http://localhost:5001](http://localhost:5001).

## Main Files

- `app.py` : Main Flask application
- `database.py` : Database setup and population
- `vector_store.py` : Vector store setup
- `definitions.py` : Configuration constants
- `requirements.txt` : Python dependencies
- `templates/index.html` : Web interface

## Notes

- The database and vector store are generated automatically and should not be committed to Git.
- Do not commit your `.env` file containing secrets.