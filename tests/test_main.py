import subprocess

def test_main_cli_help():
    # Vérifie que le script main.py s'exécute et affiche un prompt
    process = subprocess.Popen(
        ["python", "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        # Envoie 'exit' pour quitter la boucle
        stdout, stderr = process.communicate(input="exit\n", timeout=10)
        assert "Welcome to the SQL Assistant!" in stdout
    except Exception:
        process.kill()
        assert False, "main.py n'a pas répondu comme attendu"