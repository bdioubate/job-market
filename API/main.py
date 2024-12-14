from fastapi import FastAPI
from routes import router  # Import des routes depuis routes.py

# Création de l'application FastAPI
app = FastAPI(
    title="Job Market API",
    description="Une API pour récupérer et manipuler les données du marché de l'emploi.",
    version="1.0"
)

# Inclure les routes
app.include_router(router)

# Endpoint de vérification (health check)
@app.get("/", tags=["Health Check"], summary="Vérification de l'état de l'API")
def health_check():
    """
    Endpoint de vérification de l'état de l'API.
    Retourne une confirmation que l'API fonctionne correctement.
    """
    return {"status": "API is running successfully"}
