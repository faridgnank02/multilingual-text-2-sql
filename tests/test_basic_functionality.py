import pytest
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_database_manager_import():
    """Test that database manager can be imported and basic functions work."""
    try:
        import database_manager
        assert hasattr(database_manager, 'list_databases')
        assert hasattr(database_manager, 'get_active_database')
        assert hasattr(database_manager, 'ensure_directories')
    except ImportError as e:
        pytest.fail(f"Cannot import database_manager: {e}")

def test_app_import_without_openai():
    """Test that app.py imports correctly even without OpenAI key."""
    # Temporarily remove OpenAI key if it exists
    original_key = os.environ.get('OPENAI_API_KEY')
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        # Test basic imports
        from app.database import setup_database
        from app.definitions import EXPERIMENT_NAME, MODEL_ALIAS
        
        # Test database setup (should work without OpenAI)
        conn = setup_database()
        assert conn is not None
        conn.close()
        
    except Exception as e:
        pytest.fail(f"Basic app components should work without OpenAI key: {e}")
    finally:
        # Restore original key if it existed
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key

def test_project_structure():
    """Test that all required files and directories exist."""
    project_root = Path(__file__).parent.parent
    
    # Required files
    required_files = [
        'app.py',
        'database_manager.py',
        'requirements.txt',
        'README.md',
        'app/__init__.py',
        'app/database.py',
        'app/definitions.py',
        'examples/employes.csv',
        'templates/index.html'
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"Required file missing: {file_path}"

def test_database_manager_basic_functions():
    """Test database manager basic functions without external dependencies."""
    import database_manager
    
    # Test ensure_directories
    database_manager.ensure_directories()
    
    # Test get_active_database (should return default if no config)
    active = database_manager.get_active_database()
    assert isinstance(active, str)
    
    # Test list_databases (should work even with empty directory)
    databases = database_manager.list_databases()
    assert isinstance(databases, dict)