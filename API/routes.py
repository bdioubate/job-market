from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db1, get_db2
import pandas as pd


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



@router.get(
    "/job-offer-stats",
    tags=["Job Offer Stats"],
    summary="Récupère les statistiques des offres d'emploi"
)
def get_job_offer_stats(db: Session = Depends(get_db1)):
    try:
        # Requêtes SQL
        queries = {
            "pct_cdi": """
                SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE contract_type = 'CDI') / COUNT(*), 2) AS pct_cdi
                FROM jm_job;
            """,
            "pct_contract_nature": """
                SELECT ROUND(100.0 * (SELECT COUNT(*) FROM jm_job WHERE contract_nature = 'Contrat d’apprentissage') / (SELECT COUNT(*) FROM jm_job), 2) AS pct_contract_nature;
            """,
            "pct_experience_exigee": """
                SELECT ROUND(100.0 * (SELECT COUNT(*) FROM jm_job WHERE experience_required = 'E') / (SELECT COUNT(*) FROM jm_job), 2) AS pct_experience_exigee;
            """,
            "months_experience_median": """
                SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY experience_required_months) AS months_experience_median
                FROM jm_job
                WHERE experience_required_months IS NOT NULL;
            """,
            "pct_debutants": """
                SELECT ROUND(100.0 * (SELECT COUNT(*) FROM jm_job WHERE experience_required IN ('D')) / (SELECT COUNT(*) FROM jm_job), 2) AS pct_debutants;
            """,
            "mean_salary": """
                SELECT ROUND(AVG(calculated_salary), 2) AS mean_salary
                FROM jm_job
                WHERE date_creation >= '2024-01-01' AND date_creation < '2025-01-01';
            """,
            "max_salary": """
                SELECT MAX(calculated_salary) AS max_salary
                FROM jm_job;
            """,
            "total_offres": """
                SELECT COUNT(*) AS total_offres
                FROM jm_job;
            """,
            "new_offres_today": """
                SELECT COUNT(*) AS new_offres_today
                FROM jm_job
                WHERE DATE(date_creation) = CURRENT_DATE;
            """,
            "max_salary_region": """
                SELECT j.calculated_salary AS max_salary, p.departement AS max_salary_region
                FROM jm_job j
                JOIN jm_code_postaux p ON j.code_postal = p.code_postal
                ORDER BY j.calculated_salary DESC
                LIMIT 1;
            """
        }
        # Dictionnaire pour stocker les résultats
        data_dict = {}
        # Exécuter les requêtes et stocker les résultats
        for key, query in queries.items():
            try:
                result = db.execute(text(query)).fetchone()
                data_dict[key] = result[0] if result else None
            except Exception as e:
                data_dict[key] = None
        # Récupérer max_salary et max_salary_region séparément
        max_salary_region_result = db.execute(text(queries["max_salary_region"])).fetchone()
        if max_salary_region_result:
            data_dict["max_salary"] = max_salary_region_result["max_salary"]
            data_dict["max_salary_region"] = max_salary_region_result["max_salary_region"]
        else:
            data_dict["max_salary"] = None
            data_dict["max_salary_region"] = None
        # Créez un DataFrame avec une seule ligne
        df = pd.DataFrame([data_dict])
        return {"status": "success", "data": df.to_dict(orient="records")}
    except Exception as e:
        return {"detail": f"Erreur : {str(e)}"}