from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db1, get_db2


# Initialiser le routeur
router = APIRouter()

@router.get("/custom_query", tags=["Custom Queries"], summary="Récupère les données enrichies")
def get_custom_data(db: Session = Depends(get_db1)):
    query = """
        SELECT rome_code, A.rome_label, contract_type, experience_required,
               experience_required_months, departement, A.code_postal,
               date_creation, calculated_salary
        FROM jm_job A
        LEFT JOIN jm_rome B ON A.rome_label = B.rome_label
        LEFT JOIN jm_code_postaux C ON A.code_postal = C.code_postal;
    """
    try:
        results = db.execute(text(query))
        # Convertir les résultats en liste de dictionnaires
        data = [row._mapping for row in results]
        return data
    except Exception as e:
        return {"detail": f"Erreur : {str(e)}"}
    

# Route pour récupérer les métriques du modèle
@router.get(
    "/metrics",
    tags=["Metrics"],
    summary="Récupère les métriques du modèle entraîné"
)
def get_metrics_data(db: Session = Depends(get_db2)):
    """
    Effectue une requête SQL pour récupérer les métriques du modèle entraîné.
    """
    query = """
        SELECT *
        FROM metrics;
    """
    try:
        # Exécuter la requête
        results = db.execute(text(query))
        # Transformer les résultats en une liste de dictionnaires
        data = [row._mapping for row in results]
        return {"status": "success", "data": data}
    except Exception as e:
        return {"detail": f"Erreur : {str(e)}"}

