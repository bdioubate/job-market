import streamlit as st
import joblib
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(dotenv_path=".env")

# URL de l'API FastAPI
API_URL = os.getenv("API_URL")

if not API_URL:
    st.error("L'URL de l'API (API_URL) n'est pas configurée. Vérifiez le fichier .env.")
    st.stop()

# Charger le modèle
@st.cache_resource
def load_model():
    try:
        return joblib.load("salary_prediction_model.pkl")
    except FileNotFoundError:
        st.error("Le fichier salary_prediction_model.pkl est introuvable.")
        st.stop()

# Récupérer les données depuis l'API
@st.cache_data
def fetch_cleaned_data_from_api():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        
        # Vérifier si les données sont sous forme de liste de dictionnaires
        if not isinstance(data, list):
            st.error("Format inattendu des données de l'API. Les données doivent être une liste.")
            st.stop()

        return pd.DataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données depuis l'API : {e}")
        st.stop()
    except ValueError as e:
        st.error(f"Erreur de conversion des données en DataFrame : {e}")
        st.stop()

# Préparer les options utilisateur
def prepare_options(data):
    try:
        # Supprimer les doublons et créer une colonne combinée pour les options de sélection
        rome_data_unique = data.drop_duplicates(subset=['rome_code', 'rome_label']).copy()
        rome_data_unique['combined'] = rome_data_unique['rome_code'] + ' - ' + rome_data_unique['rome_label']

        contract_type_options = data['contract_type'].drop_duplicates().tolist()
        experience_required_options = data['experience_required'].drop_duplicates().tolist()
        experience_required_months_options = data['experience_required_months'].drop_duplicates().sort_values().tolist()
        job_location_options = data['code_postal'].drop_duplicates().tolist()
        return rome_data_unique, contract_type_options, experience_required_options, experience_required_months_options, job_location_options
    except KeyError as e:
        st.error(f"Les données retournées par l'API sont manquantes ou incorrectes : {e}")
        st.stop()

# Fonction principale pour l'application Streamlit
def main():
    st.title("Prédiction de Salaire")

    # Récupérer les données nettoyées depuis l'API
    cleaned_data = fetch_cleaned_data_from_api()

    # Charger le modèle
    model = load_model()

    # Préparer les listes déroulantes
    rome_data_unique, contract_type_options, experience_required_options, \
        experience_required_months_options, job_location_options = prepare_options(cleaned_data)

    # Widgets pour la saisie utilisateur
    rome_code_selected = st.selectbox('Sélectionnez le code ROME :', rome_data_unique['combined'])
    rome_code_actual = rome_code_selected.split(' - ')[0]

    contract_type = st.selectbox("Type de Contrat", contract_type_options)
    experience_required = st.selectbox("Expérience Requise", experience_required_options)
    experience_required_months = st.selectbox("Mois d'Expérience", experience_required_months_options)
    job_location_code = st.selectbox("Code Postal", job_location_options)

    # Bouton pour lancer la prédiction
    if st.button("Prédire le Salaire"):
        try:
            # Extraire le département des deux premiers chiffres du code postal
            job_location_department = str(job_location_code).zfill(2)[:2]

            # Préparer les données pour la prédiction
            input_data = pd.DataFrame({
                'rome_code': [rome_code_actual],
                'contract_type': [contract_type],
                'experience_required': [experience_required],
                'experience_required_months': [experience_required_months],
                'departement': [job_location_department],
                'code_postal': [job_location_code]
            })

            # Nettoyer et convertir les types
            input_data['rome_code'] = input_data['rome_code'].astype(str)
            input_data['contract_type'] = input_data['contract_type'].astype(str)
            input_data['experience_required'] = input_data['experience_required'].astype(str)
            input_data['experience_required_months'] = pd.to_numeric(input_data['experience_required_months'], errors='coerce').fillna(0).astype(float)
            input_data['departement'] = input_data['departement'].astype(str)
            input_data['code_postal'] = input_data['code_postal'].astype(str)

            # Faire la prédiction
            prediction = model.predict(input_data)
            st.success(f"Salaire Prévu : {prediction[0]:.2f} €")
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
            st.write("Détails :", e)

if __name__ == "__main__":
    main()
