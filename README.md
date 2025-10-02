# 🌐 Multilingual Text-to-SQL Generator

A comprehensive web application that converts natural language questions (in multiple languages) into SQL queries and executes them on customizable databases. Built with Flask, LangChain, LangGraph, OpenAI GPT-4o-mini, and FAISS vector search.

## Key Features

### 🌍 **Multilingual Support**
- **Multi-language support**: French, English, Spanish, German, and many more languages supported by GPT-4o-mini
- **Auto-detection**: Automatically detects input language
- **Smart translation**: Translates to English for optimal SQL generation
- **Unlimited language capability**: Leverages GPT-4o-mini's extensive language understanding

### **Flexible Database Management**
- **Web upload interface**: Upload SQL files, CSV data, or SQLite databases directly
- **Multiple formats**: Support for `.sql`, `.csv`, `.db` files
- **Dynamic switching**: Change active database through web interface
- **Security validation**: File type checking and sanitization

### **Advanced SQL Generation**
- **LangChain workflow**: Sophisticated query processing pipeline
- **Vector search**: FAISS-powered semantic search for SQL documentation
- **Safety checks**: Multiple layers of SQL injection protection
- **Query explanation**: Detailed explanations of generated queries

### **Production-Ready**
- **MLflow integration**: Model versioning and experiment tracking
- **CI/CD pipeline**: Automated testing with GitHub Actions
- **Comprehensive testing**: 9 test suites covering all functionality
- **Docker support**: Containerized deployment ready

##  Latest Updates

###  **Version 2.0 Features**
- **Web Upload System**: Direct database upload through browser interface
- **Enhanced UI**: Restructured interface with "Query Explanation" section at bottom
- **Database Manager CLI**: Complete command-line tool for database management
- **Multi-format Support**: CSV, SQL, SQLite database imports
- **Real-time Database Info**: Active database indicator and table statistics
- **GitHub Actions CI/CD**: Automated testing and deployment pipeline

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- MLflow (for model management and experiment tracking)

### 1. Clone the Repository
```bash
git clone https://github.com/faridgnank02/multilingual-text-2-sql.git
cd multilingual-text-2-sql
```

### 2. Set Up Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
# On Windows: set OPENAI_API_KEY=your-api-key-here
```

### 4. Start MLflow Server
```bash
# Launch MLflow UI (required for model loading)
mlflow ui

# MLflow will be available at http://localhost:5000
# Keep this terminal open and proceed in a new terminal
```

### 5. Launch Application

#### Option A: Use Default Database
```bash
python3 app.py
```

#### Option B: Import Your Own Data First
```bash
# Import example database
python3 database_manager.py import examples/bibliotheque.sql bibliotheque

# Activate the new database
python3 database_manager.py activate bibliotheque

# Launch application
python3 app.py
```

🌐 **Access the application**: [http://localhost:5000](http://localhost:5000)
📊 **Monitor experiments**: MLflow UI at [http://localhost:5000](http://localhost:5000) (if running)

## Database Management

### Web Interface Upload
Upload databases directly through the web interface:
1. **Visit the application** at [http://localhost:5000](http://localhost:5000)
2. **Use the upload section** to select your file (.sql, .csv, .db)
3. **File validation** ensures security and compatibility
4. **Automatic processing** imports and activates your database
5. **Real-time feedback** shows database information and table statistics

### Command Line Management

#### Import Data
```bash
# Import CSV file
python3 database_manager.py import data.csv my_database

# Import SQL script
python3 database_manager.py import schema.sql my_database

# Import SQLite database
python3 database_manager.py import database.db my_database
```

#### Database Operations
```bash
# List all available databases
python3 database_manager.py list

# Switch active database
python3 database_manager.py activate database_name

# View database details
python3 database_manager.py info database_name
```

### Supported File Formats
- **`.sql`** - SQL scripts with CREATE TABLE and INSERT statements
- **`.csv`** - Comma-separated values (auto-detects schema)
- **`.db`** - SQLite database files

## Example Databases & Test Cases

The project includes 3 ready-to-use example databases with multilingual test questions:

### Library Database (`examples/bibliotheque.sql`)
```bash
python3 database_manager.py import examples/bibliotheque.sql library
python3 database_manager.py activate library
```
**Test Questions (examples in 4+ languages):**
- 🇫🇷 "Combien de livres sont actuellement empruntés ?" 
- 🇬🇧 "How many books are currently borrowed?"
- 🇪🇸 "¿Cuántos libros están prestados actualmente?"
- 🇩🇪 "Wie viele Bücher sind derzeit ausgeliehen?"
- 🇮🇹 "Quanti libri sono attualmente prestati?"
- 🇵🇹 "Quantos livros estão atualmente emprestados?"
- *And many more languages supported by GPT-4o-mini...*

### School Database (`examples/ecole.sql`) 
```bash
python3 database_manager.py import examples/ecole.sql school
python3 database_manager.py activate school
```
**Test Questions:**
- 🇫🇷 "Quelle est la moyenne de l'étudiant Alice Martin ?"
- 🇬🇧 "What is Alice Martin's average grade?"
- 🇪🇸 "¿Cuál es el promedio de la estudiante Alice Martin?"
- 🇩🇪 "Wie ist der Durchschnitt der Studentin Alice Martin?"

### 👥 Employee Database (`examples/employes.csv`)
```bash
python3 database_manager.py import examples/employes.csv employees
python3 database_manager.py activate employees
```
**Test Questions:**
- 🇫🇷 "Quel est le salaire moyen par département ?"
- 🇬🇧 "What is the average salary by department?"
- 🇪🇸 "¿Cuál es el salario promedio por departamento?"
- 🇩🇪 "Wie hoch ist das Durchschnittsgehalt nach Abteilung?"

## Architecture

### Core Components
```
multilingual-text-2-sql/
├── app.py                    # Main Flask web application
├── database_manager.py       # Complete CLI database management tool
├── main.py                   # CLI interface for direct query processing
├── register_model.py         # MLflow model registration
├── app/                      # Core application modules
│   ├── workflow.py           #   LangChain workflow orchestration
│   ├── database.py           #   Database connection & operations
│   ├── vector_store.py       #   FAISS vector store management
│   ├── sql_generation.py     #   SQL query generation logic
│   └── definitions.py        #   Configuration constants
├── templates/                #   Web interface templates
│   └── index.html            #   Enhanced UI with upload system
├── tests/                    #  Comprehensive test suite
│   ├── test_basic_functionality.py
│   ├── test_database.py
│   ├── test_vector_store.py
│   ├── test_workflow.py
│   └── test_main.py
├── examples/                 #  Sample databases
├── data/                     #  Database and vector store storage
└── .github/workflows/        # CI/CD pipeline
```

### Tech Stack
- **Backend**: Flask, Python 3.8+
- **AI/ML**: OpenAI GPT-4o-mini, LangChain, LangGraph
- **Database**: SQLite with dynamic schema support
- **Search**: FAISS vector store for semantic search
- **ML Ops**: MLflow for model management and experiment tracking
- **Testing**: pytest with comprehensive coverage
- **CI/CD**: GitHub Actions with automated testing

## MLflow Integration

The application uses MLflow for model management and experiment tracking:

### Starting MLflow
```bash
# Launch MLflow server (required)
mlflow ui

# Access MLflow UI
open http://localhost:5000
```

### Features
- **Model Versioning**: Track different versions of the SQL generation model
- **Experiment Tracking**: Monitor query generation performance
- **Model Registry**: Centralized model management
- **Metrics Logging**: Track query success rates and processing times

### MLflow Directory Structure
```
mlruns/
├── 0/                      # Default experiment
├── experiments/            # Custom experiments  
└── models/                # Registered models
    └── sql_generator_model/
```

## Testing & Quality Assurance

### Run Tests
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test categories
python3 -m pytest tests/test_database.py -v
python3 -m pytest tests/test_workflow.py -v

# Simulate CI/CD environment
python3 test_ci_simulation.py
```

### Test Coverage
- **Database operations** - Connection, import, switching
- **Web interface** - Upload processing, file validation
- **Multilingual processing** - Translation, query generation
- **Vector store** - Semantic search, document indexing
- **CLI tools** - Database management commands
- **Error handling** - Graceful failure modes
- **Security** - SQL injection prevention, file validation

## Deployment

### Docker Deployment
```bash
# Build image
docker build -t multilingual-text2sql .

# Run container
docker run -p 5000:5000 -e OPENAI_API_KEY=your-key multilingual-text2sql
```

### Production Environment
```bash
# Set production environment variables
export FLASK_ENV=production
export OPENAI_API_KEY=your-production-key

# Start MLflow server (required in production)
mlflow server --host 0.0.0.0 --port 5001 &

# Launch with production server
gunicorn --bind 0.0.0.0:5000 app:app
```

**⚠️ Important**: MLflow server must be running before starting the Flask application, as the app loads models from the MLflow model registry during initialization.

## Security Features

- **File Upload Validation**: Strict file type checking and sanitization
- **SQL Injection Protection**: Multiple layers of query validation
- **Input Sanitization**: Comprehensive cleaning of user inputs
- **Error Handling**: Graceful failure without information leakage
- **API Key Management**: Secure environment variable handling

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with comprehensive tests
4. **Run the test suite**: `python3 -m pytest tests/ -v`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenAI** for GPT-4o-mini language model
- **LangChain** for workflow orchestration framework
- **FAISS** for efficient vector similarity search
- **MLflow** for experiment tracking and model management
