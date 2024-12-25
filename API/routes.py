from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db  # Importer la session de la base de données

# Initialiser le routeur
router = APIRouter()

@router.get("/custom_query", tags=["Custom Queries"], summary="Récupère les données enrichies")
def get_custom_data(db: Session = Depends(get_db)):
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
