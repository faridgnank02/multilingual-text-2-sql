# 🚀 Startup Guide - Multilingual Text-to-SQL

This guide details the correct order to start the **multilingual-text-2-sql** project.

## 📋 Prerequisites

1. **Python 3.8+** installed on your system
2. **OpenAI API key** configured
3. **Dependencies installed** (see Installation section)

## 🔧 Dependencies Installation

```bash
# 1. Clone the project
git clone https://github.com/faridgnank02/multilingual-text-2-sql.git
cd multilingual-text-2-sql

# 2. Install all required dependencies
pip3 install -r requirements.txt

# 3. Configure OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
# On Windows: set OPENAI_API_KEY=your-api-key-here
```

## 🚦 Correct Startup Sequence

### Step 1: Database Initialization
```bash
# Test database initialization
python3 -c "from app.database import setup_database; conn = setup_database(); print('✅ Database ready'); conn.close()"
```

### Step 2: Vector Store Preparation
```bash
# Test vector store module import
python3 -c "from app.vector_store import setup_vector_store; print('✅ Vector store module ready')"
```

### Step 3: MLflow Model Registration
```bash
# Register model in MLflow (REQUIRED before launching app)
python3 register_model.py
```
**✅ Expected output:**
```
Model registered successfully!
Model Name: sql_generator_model, Alias: Production
```

### Step 4: Application Launch

#### Option A: Flask Web Application
```bash
python3 app.py
```
**🌐 Access:** [http://localhost:5001](http://localhost:5001)

#### Option B: CLI Interface
```bash
python3 main.py
```

## 🔍 Important Verifications

### ✅ MLflow Model Registered
Verify that the model is correctly registered:
```bash
python3 -c "
import mlflow
from app.definitions import REGISTERED_MODEL_NAME, MODEL_ALIAS, REMOTE_SERVER_URI
mlflow.set_tracking_uri(REMOTE_SERVER_URI)
model_uri = f'models:/{REGISTERED_MODEL_NAME}@{MODEL_ALIAS}'
model = mlflow.pyfunc.load_model(model_uri)
print('✅ Model loaded successfully')
"
```

### ✅ Database Structure
```bash
# List available databases
python3 database_manager.py list

# View active database
python3 -c "from app.database_manager import get_active_database; print(f'Active DB: {get_active_database()}')"
```

## ⚠️ Common Errors and Solutions

### 1. "Model not found" Error
**Cause:** Model not registered in MLflow
**Solution:** Run `python3 register_model.py` before launching the application

### 2. "No module named 'bs4'" Error
**Cause:** Missing dependencies
**Solution:** 
```bash
pip3 install beautifulsoup4
pip3 install -r requirements.txt
```

### 3. "langchain module not found" Error
**Cause:** Incomplete dependency installation
**Solution:** 
```bash
pip3 install -r requirements.txt
```

### 4. MLflow Connection Error
**Cause:** MLflow tracking server not accessible
**Solution:** Local MLflow server (port 5000) is automatically used by the application

## 🏃‍♂️ Quick Start (Complete Script)

```bash
#!/bin/bash
# Complete startup script

echo "🚀 Starting Multilingual Text-to-SQL..."

# 1. API Key verification
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY not configured"
    echo "Run: export OPENAI_API_KEY='your-api-key-here'"
    exit 1
fi

# 2. Dependencies installation
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# 3. Database initialization
echo "🗄️ Initializing database..."
python3 -c "from app.database import setup_database; setup_database()"

# 4. Model registration
echo "🤖 Registering MLflow model..."
python3 register_model.py

# 5. Application launch
echo "🌐 Starting web application..."
python3 app.py
```

## 📚 Additional Information

- **Application Port:** 5001 (Flask)
- **MLflow Port:** 5000 (automatic)
- **Default Database:** `data/databases/default.db`
- **Vector Store:** `data/vector_store/`
- **MLflow Model:** `sql_generator_model@Production`

## 🎯 Key Points to Remember

1. **Model registration (`register_model.py`) is MANDATORY** before launching the application
2. **Initialization order is important**: Database → Vector Store → Model → Application
3. **All dependencies must be installed** with `pip3 install -r requirements.txt`
4. **OpenAI API key must be configured** before startup
5. **The application automatically manages** the connection to the local MLflow server

---
**✅ Your analysis was correct!** The Database → Vector Store → register_model.py → app.py order is indeed the optimal sequence to start the project.