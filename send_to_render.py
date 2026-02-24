import psycopg2  # La bibliothèque que Django utilise pour PostgreSQL
import sys

# Votre URL de connexion Render
url = "postgresql://annuaire_mosquee_user:VorKSHeAyvLzdan3sJsjlFA5THIRe7dr@dpg-d65qghmsb7us73dsph40-a.frankfurt-postgres.render.com/annuaire_mosquee"

try:
    print("Connexion à Render...")
    conn = psycopg2.connect(url)
    conn.autocommit = True
    cursor = conn.cursor()

    print("Lecture du fichier SQL...")
    with open('render_database.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    print("Envoi des données (cela peut prendre un instant)...")
    cursor.execute(sql)

    print("Félicitations ! Votre base Render est à jour.")
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Erreur : {e}")