#!/usr/bin/env python3
"""
Script de test local - Simule l'environnement GitHub Actions
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Exécute une commande et affiche le résultat."""
    print(f"\n🔧 {description}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr.strip():
                print("STDERR:", result.stderr)
            if result.stdout.strip():
                print("STDOUT:", result.stdout)
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def simulate_github_actions():
    """Simule l'environnement GitHub Actions localement."""
    
    print("🧪 SIMULATION GITHUB ACTIONS - TESTS LOCAUX")
    print("=" * 70)
    
    # 1. Vérifier la structure du projet
    print("\n📁 Vérification de la structure du projet")
    required_files = [
        'app.py', 'database_manager.py', 'requirements.txt',
        'app/database.py', 'tests/test_database.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Fichiers manquants: {missing_files}")
        return False
    else:
        print("✅ Structure du projet OK")
    
    # 2. Créer l'environnement de test
    print("\n🔧 Création de l'environnement de test")
    os.makedirs("data/custom_databases", exist_ok=True)
    os.makedirs("temp_uploads", exist_ok=True)
    
    # Sauvegarder la clé OpenAI existante
    original_key = os.environ.get('OPENAI_API_KEY')
    
    # Créer un fichier .env de test (sans vraie clé)
    with open('.env', 'w') as f:
        f.write("OPENAI_API_KEY=sk-dummy-key-for-testing\n")
    
    print("✅ Environnement de test créé")
    
    # 3. Tests d'import
    tests = []
    
    tests.append(run_command(
        "python -c \"import database_manager; print('Database manager import OK')\"",
        "Test import database_manager"
    ))
    
    tests.append(run_command(
        "python -c \"from app.database import setup_database; print('App database import OK')\"",
        "Test import app.database"
    ))
    
    tests.append(run_command(
        "python -c \"import app; print('App import OK')\"",
        "Test import app"
    ))
    
    # 4. Tests pytest
    tests.append(run_command(
        "python -m pytest tests/test_database.py -v",
        "Test database"
    ))
    
    tests.append(run_command(
        "python -m pytest tests/test_basic_functionality.py -v",
        "Test fonctionnalités de base"
    ))
    
    # Tests avec skip pour les APIs manquantes
    tests.append(run_command(
        "python -m pytest tests/test_vector_store.py -v",
        "Test vector store (avec skip si pas d'API)"
    ))
    
    tests.append(run_command(
        "python -m pytest tests/test_workflow.py -v", 
        "Test workflow (avec skip si pas d'API)"
    ))
    
    tests.append(run_command(
        "python -m pytest tests/test_main.py -v",
        "Test main (avec skip si pas d'API)"
    ))
    
    # 5. Test database manager CLI
    tests.append(run_command(
        "python database_manager.py list",
        "Test database manager CLI"
    ))
    
    # Restaurer l'environnement
    if original_key:
        os.environ['OPENAI_API_KEY'] = original_key
    
    # Résumé
    print("\n📊 RÉSUMÉ DES TESTS")
    print("=" * 70)
    
    passed = sum(tests)
    total = len(tests)
    
    print(f"✅ Tests réussis: {passed}/{total}")
    print(f"❌ Tests échoués: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 TOUS LES TESTS PASSENT - PRÊT POUR GITHUB ACTIONS!")
        return True
    else:
        print(f"\n⚠️ {total - passed} test(s) échoué(s) - À corriger avant push")
        return False

if __name__ == "__main__":
    success = simulate_github_actions()
    sys.exit(0 if success else 1)