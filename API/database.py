from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(dotenv_path="../.env") 

# URL de connexion à la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurer SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test de connexion et récupération des données
if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("Connexion réussie à la base de données !")
            
            # Requête pour tester la base de données
            query = text("SELECT * FROM jm_job LIMIT 5;")  # Remplacez `jm_job` par le nom d'une table existante
            result = connection.execute(query)
            
            print("Données récupérées :")
            for row in result:
                print(row)
                
    except Exception as e:
        print(f"Erreur de connexion : {e}")
