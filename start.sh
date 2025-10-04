#!/bin/bash

# Automatic Startup Script - Multilingual Text-to-SQL
# This script automates the complete project startup sequence

set -e  # Stop script on error

echo "🚀 Starting Multilingual Text-to-SQL..."
echo "=========================================="

# Colors for display
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display colored messages
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "ℹ️  $1"; }

# 1. OpenAI API Key verification
print_info "1. Checking OpenAI API key..."
if [ -z "$OPENAI_API_KEY" ]; then
    print_error "OPENAI_API_KEY not configured"
    echo "Run: export OPENAI_API_KEY='your-api-key-here'"
    exit 1
else
    print_success "OpenAI API key configured"
fi

# 2. Python verification
print_info "2. Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION detected"
else
    print_error "Python 3 not found"
    exit 1
fi

# 3. Dependencies installation
print_info "3. Installing/Checking dependencies..."
if [ -f "requirements.txt" ]; then
    python3 -c "import langchain, mlflow, flask" 2>/dev/null || {
        print_warning "Installing missing dependencies..."
        pip3 install -r requirements.txt
    }
    print_success "Dependencies installed"
else
    print_error "requirements.txt file not found"
    exit 1
fi

# 4. Database initialization
print_info "4. Initializing database..."
python3 -c "
from app.database import setup_database
conn = setup_database()
conn.close()
print('Database initialized')
" || {
    print_error "Database initialization failed"
    exit 1
}
print_success "Database ready"

# 5. Vector store test
print_info "5. Checking Vector Store module..."
python3 -c "
from app.vector_store import setup_vector_store
print('Vector Store module verified')
" || {
    print_error "Vector Store module failed"
    exit 1
}
print_success "Vector Store module ready"

# 6. MLflow model registration
print_info "6. Registering MLflow model..."
python3 register_model.py > /dev/null 2>&1 || {
    print_error "Model registration failed"
    exit 1
}
print_success "MLflow model registered"

# 7. Model loading test
print_info "7. Verifying model loading..."
python3 -c "
import mlflow
from app.definitions import REGISTERED_MODEL_NAME, MODEL_ALIAS, REMOTE_SERVER_URI
mlflow.set_tracking_uri(REMOTE_SERVER_URI)
model_uri = f'models:/{REGISTERED_MODEL_NAME}@{MODEL_ALIAS}'
model = mlflow.pyfunc.load_model(model_uri)
print('Model loaded successfully')
" > /dev/null 2>&1 || {
    print_error "Model loading failed"
    exit 1
}
print_success "MLflow model validated"

# 8. Display startup information
print_info "8. System information..."
python3 -c "
from app.database_manager import get_active_database, list_databases
active_db = get_active_database()
databases = list_databases()
print(f'Active database: {active_db}')
print(f'Available databases: {len(databases)}')
print('System ready to start!')
"

echo "=========================================="
print_success "🎯 Initialization completed successfully!"
echo ""
print_info "Startup options:"
echo "  • Web Application : python3 app.py"
echo "  • CLI Interface   : python3 main.py"
echo ""
print_info "Web Access : http://localhost:5001"
echo "=========================================="

# 9. Automatic startup request
read -p "Start web application now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[YyOo]$ ]]; then
    print_info "🌐 Starting web application..."
    python3 app.py
fi