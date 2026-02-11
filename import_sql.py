import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_import():
    # L'URL de votre base de données Render est dans la variable d'environnement
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL non définie. Arrêt.")
        sys.exit(1)

    sql_file_path = 'sql/converted.sql'

    try:
        # Connexion à la base Render
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        print(f"[INFO] Lecture du fichier {sql_file_path}...")
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        print("[INFO] Exécution du script SQL (cela peut prendre un moment)...")
        cur.execute(sql_script)
        print("✅ Script SQL exécuté avec succès.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_import()