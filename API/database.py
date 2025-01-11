from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(dotenv_path="../.env")

#Chaine de connecion pour acceder a la base de données pour recupérer les informations metiers dont l'utilisateur aura besoin pour s'orienter
# Base de données 1
DATABASE_URL = os.getenv("DATABASE_URL")
engine1 = create_engine(DATABASE_URL)
SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
Base1 = declarative_base()

#Chaine de connecion pour acceder a la base de données pour accéder aux resultats de notre modele de machine learning
# Base de données 2
DATABASE_URL2 = os.getenv("DATABASE_URL2")
engine2 = create_engine(DATABASE_URL2)
SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
Base2 = declarative_base()

# Fonction pour obtenir une session pour chaque base de données
def get_db1():
    db = SessionLocal1()
    try:
        yield db
    finally:
        db.close()

def get_db2():
    db = SessionLocal2()
    try:
        yield db
    finally:
        db.close()

# Test de connexion pour les deux bases de données
if __name__ == "__main__":
    try:
        # Test connexion à la première base de données
        with engine1.connect() as connection1:
            print("Connexion réussie à la base de données 1 !")
            query1 = text("SELECT * FROM jm_job LIMIT 5;")  # Remplacez `jm_job` par une table de la base 1
            result1 = connection1.execute(query1)
            print("Données récupérées de la base 1 :")
            for row in result1:
                print(row)
        
        # Test connexion à la deuxième base de données
        with engine2.connect() as connection2:
            print("Connexion réussie à la base de données 2 !")
            query2 = text("SELECT * FROM metrics LIMIT 2;")  # Remplacez `autre_table` par une table de la base 2
            result2 = connection2.execute(query2)
            print("Données récupérées de la base 2 :")
            for row in result2:
                print(row)

    except Exception as e:
        print(f"Erreur de connexion : {e}")

