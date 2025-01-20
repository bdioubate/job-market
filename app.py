import streamlit as st
import joblib
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

# Charger les variables d'environnement
load_dotenv(dotenv_path=".env")

# URLs de l'API FastAPI
API_URL = os.getenv("API_URL")
API_URL_STATS = os.getenv("API_URL_STATS")

if not API_URL:
    st.error("L'URL de l'API (API_URL) n'est pas configurée. Vérifiez le fichier .env.")
    st.stop()

if not API_URL_STATS:
    st.error("L'URL de l'API (API_URL_STATS) n'est pas configurée. Vérifiez le fichier .env.")
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
    with st.spinner("Chargement des données depuis l'API, veuillez patienter..."):
        try:
            response = requests.get(API_URL, timeout=60)  # Timeout ajouté
            response.raise_for_status()
            data = response.json()

            if isinstance(data, dict) and "results" in data:
                data = data["results"]

            if not isinstance(data, list):
                raise ValueError("Les données doivent être une liste ou contenir une clé 'results'.")

            return pd.DataFrame(data)
        except requests.exceptions.Timeout:
            st.error("Le temps de réponse de l'API est trop long. Réessayez plus tard.")
            st.stop()
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données : {e}")
            st.stop()

@st.cache_data
def fetch_job_offer_stats():
    """
    Récupère les statistiques des offres d'emploi depuis l'API.
    """
    try:
        response = requests.get(API_URL_STATS, timeout=60)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            return data.get("data", {})
        else:
            st.warning("Impossible de récupérer les statistiques.")
            return {}
    except Exception as e:
        st.error(f"Erreur lors de la récupération des statistiques : {e}")
        return {}

@st.cache_data
def fetch_model_metrics():
    """
    Récupère les métriques du modèle depuis l'API.
    """
    METRICS_API_URL = "https://job-market-api.onrender.com/metrics"
    try:
        response = requests.get(METRICS_API_URL, timeout=60)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            return pd.DataFrame(data.get("data", []))
        else:
            st.warning("Impossible de récupérer les métriques du modèle.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors de la récupération des métriques : {e}")
        return pd.DataFrame()



# Fonction pour valider les champs
def validate_field(field_value, default="Veuillez sélectionner une option", error_message=""):
    """
    Valide un champ pour s'assurer qu'il ne contient pas la valeur par défaut.
    
    Parameters:
        field_value (str): La valeur sélectionnée par l'utilisateur.
        default (str): La valeur par défaut indiquant qu'aucune sélection n'a été faite.
        error_message (str): Le message d'erreur à afficher si la validation échoue.
    
    Returns:
        bool: True si la validation est réussie, False sinon.
    """
    if field_value == default:
        st.markdown(f"<span style='color:red;'>{error_message}</span>", unsafe_allow_html=True)
        return False
    return True


# Préparer les options utilisateur
def prepare_options(data):
    try:
        rome_data_unique = data.drop_duplicates(subset=['rome_code', 'rome_label']).dropna(subset=['rome_code', 'rome_label']).copy()
        rome_data_unique['combined'] = rome_data_unique['rome_code'] + ' - ' + rome_data_unique['rome_label']

        contract_type_descriptions = {
            "CDI": "Contrat à Durée Indéterminée",
            "MIS": "Mission Intérim",
            "CDD": "Contrat à Durée Déterminée",
            "LIB": "Libéral",
            "FRA": "Freelance",
            "DIN": "Détachement International",
            "SAI": "Stage avec Indemnité",
            "CCE": "Contrat de Collaboration Externe"
        }

        contract_type_options_raw = data['contract_type'].drop_duplicates().tolist()
        contract_type_options = [
            f"{contract} - {contract_type_descriptions.get(contract, 'Description non disponible')}"
            for contract in contract_type_options_raw
        ]

        experience_required_options = data['experience_required'].drop_duplicates().tolist()
        experience_required_months_options = data['experience_required_months'].drop_duplicates().sort_values().tolist()
        job_location_options = data['code_postal'].drop_duplicates().tolist()
        return rome_data_unique, contract_type_options, experience_required_options, experience_required_months_options, job_location_options
    except KeyError as e:
        st.error(f"Les données retournées par l'API sont incorrectes ou manquantes : {e}")
        st.stop()

# Fonction pour afficher un graphique
def plot_salary_distribution(data):
    fig, ax = plt.subplots()
    sns.histplot(data['calculated_salary'], kde=True, ax=ax)
    ax.set_title("Distribution des Salaires")
    ax.set_xlabel("Salaire")
    ax.set_ylabel("Fréquence")
    st.pyplot(fig)

# Fonction principale
def main():
    style = "<style>h1 {text-align: center;}</style>"
    st.markdown(style, unsafe_allow_html=True)
    st.title("VOTRE CARRIÈRE, NOTRE OBSESSION !")

    # Ajouter un texte introductif
    #<h2 style="text-align: center; color: #2C3E50;">VOTRE CARRIÈRE, NOTRE OBSESSION !</h2>
    st.markdown("""
        <h2 style="text-align: center; font-size: 20px; color: #34495E;">
            Vous êtes étudiant ? Vous cherchez à changer de job ou à négocier une augmentation ?
            Notre outil de prédiction est là pour vous donner des <b>insights éclairés</b> !
        </h2>
    """, unsafe_allow_html=True)

    stats = fetch_job_offer_stats()

    pourcentage_cdi = stats.get("pourcentage_cdi", "N/A")
    mean_salary = stats.get("mean_salary", "N/A")
    max_salary = stats.get("max_salary", "N/A")
    total_offres = stats.get("total_offres", "N/A")
    max_salary_region = stats.get("max_salary_region", "N/A")
    max_salary_r = stats.get("max_salary_r", "N/A")

    # Ajouter les "Fun Facts" avec les variables dynamiques
    st.markdown(f"""
        <h3 style="color: #2980B9; text-align: center; font-size: 24px;">FUN FACTS :</h3>
        <ul style="font-size: 20px; color: #34495E; text-align: center; width: 100%;">
            <p>Saviez-vous que <b style="color: red;">{pourcentage_cdi}%</b> des offres actuelles sont des CDI ? La sécurité de l'emploi est à portée de main !</p></br>
            <p>Actuellement, <b style="color: red;">{stats.get("pourcentage_contract_nature", "N/A")}%</b> des offres étudiées sont des contrats d'apprentissage. Une opportunité idéale pour apprendre en travaillant !</p></br>
            <p>Aujourd'hui, <b style="color: red;">{stats.get("pourcentage_experience_exigee", "N/A")}%</b> des offres exigent une expérience professionnelle. Préparez-vous à valoriser vos années de dur labeur !</p></br>
            <p>Une expérience de plus de <b style="color: red;">{stats.get("months_experience_median", "N/A")}</b> mois est demandée en moyenne par les employeurs.</br>Êtes-vous à la hauteur ?</p></br>
            <p>Bonne nouvelle pour les débutants : <b style="color: red;">{stats.get("pourcentage_debutants", "N/A")}%</b> des offres acceptent les candidats sans expérience préalable. Lancez-vous !</p></br>
            <p>Le salaire moyen proposé dans notre base de données est de <b style="color: red;">{mean_salary} euros</b> par an.</br>Où vous situez-vous ?</p></br>
            <p>Les offres les plus généreuses atteignent jusqu'à <b style="color: red;">{max_salary} euros</b> par an. Visez toujours plus haut !</p></br>
            <p>En ce moment, nous avons un total de <b style="color: red;">{total_offres}</b> offres d'emploi étudiées.</p></br>
            <p><b style="color: red;">{stats.get("new_offres_today", "N/A")}</b> nouvelles offres ont été postées aujourd'hui. Ne laissez pas passer votre chance !</p></br>
            <p>Les plus gros salaires sont proposés dans le département <b style="color: red;">{max_salary_region}</b>, où l'offre atteint <b style="color: red;">{max_salary_r} euros</b> par an. Alors, prêt(e) à déménager ?</p></br>
        </ul>
    """, unsafe_allow_html=True)


    cleaned_data = fetch_cleaned_data_from_api()


    plot_salary_distribution(cleaned_data)

    # Récupérer les métriques
    metrics_data = fetch_model_metrics()

    if not metrics_data.empty:
        # Trier les métriques par date et sélectionner la dernière entrée
        latest_metrics = metrics_data.sort_values(by="date_creation", ascending=False).iloc[0]

        # Phrase descriptive basée sur les dernières métriques
        st.markdown(f"""
            <h3 style="color: #2980B9; text-align: center;">Performance du Modèle :</h3>
            <p style="font-size: 18px; color: #34495E; text-align: center;">
                Notre modèle a été évalué récemment avec les résultats suivants :
                <b>MSE</b>: {latest_metrics['mse']:.2f}, 
                <b>RMSE</b>: {latest_metrics['rmse']:.2f}, 
                <b>R²</b>: {latest_metrics['r2']:.2f}, 
                <b>MAE</b>: {latest_metrics['mae']:.2f}.
            </p>
        """, unsafe_allow_html=True)

        # Configuration des styles globaux
        sns.set_theme(style="whitegrid")

        # Ajout du sommaire en haut de la section
        st.markdown("""
        ### Sommaire des métriques
        - **MSE (Mean Squared Error)** : Mesure l'erreur quadratique moyenne, sensible aux grandes erreurs.
        - **RMSE (Root Mean Squared Error)** : Racine carrée de la MSE, exprime l'erreur en unités d'origine.
        - **R² (Coefficient de Détermination)** : Indique la qualité de l'ajustement (plus proche de 1, mieux c'est).
        - **MAE (Mean Absolute Error)** : Moyenne des erreurs absolues, moins sensible aux valeurs aberrantes.
        """, unsafe_allow_html=False)

        # Création des graphiques
        # MSE - Line Plot
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=metrics_data, x='date_creation', y='mse', marker="o", color="#1f77b4", linewidth=2.5, ax=ax1)
        ax1.set_title("Évolution de la MSE (Mean Squared Error)", fontsize=16, color="#1f77b4")
        ax1.set_xlabel("Date", fontsize=12)
        ax1.set_ylabel("MSE", fontsize=12)
        ax1.grid(True, linestyle="--", alpha=0.7)
        plt.xticks(rotation=45)
        st.pyplot(fig1)

        # RMSE - Bar Plot
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.barplot(data=metrics_data, x='date_creation', y='rmse', palette="viridis", ax=ax2)
        ax2.set_title("Évolution de la RMSE (Root Mean Squared Error)", fontsize=16, color="#ff7f0e")
        ax2.set_xlabel("Date", fontsize=12)
        ax2.set_ylabel("RMSE", fontsize=12)
        ax2.grid(True, linestyle="--", alpha=0.7)
        plt.xticks(rotation=45)
        st.pyplot(fig2)

        # R² - Scatter Plot
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=metrics_data, x='date_creation', y='r2', color="#2ca02c", s=120, edgecolor="black", ax=ax3)
        ax3.set_title("Évolution du R² (Coefficient de Détermination)", fontsize=16, color="#2ca02c")
        ax3.set_xlabel("Date", fontsize=12)
        ax3.set_ylabel("R²", fontsize=12)
        ax3.grid(True, linestyle="--", alpha=0.7)
        plt.xticks(rotation=45)
        st.pyplot(fig3)

        # MAE - Line Plot with Dashed Style
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=metrics_data, x='date_creation', y='mae', marker="s", color="#d62728", linewidth=2.5, linestyle="--", ax=ax4)
        ax4.set_title("Évolution de la MAE (Mean Absolute Error)", fontsize=16, color="#d62728")
        ax4.set_xlabel("Date", fontsize=12)
        ax4.set_ylabel("MAE", fontsize=12)
        ax4.grid(True, linestyle="--", alpha=0.7)
        plt.xticks(rotation=45)
        st.pyplot(fig4)


    # Ajout du texte avant le formulaire
    st.markdown("""
        <h3 style="text-align: center; color: #2980B9;">Prêt à découvrir votre valeur cachée ? C’est parti !</h3>
    """, unsafe_allow_html=True)

    
    model = load_model()

    rome_data_unique, contract_type_options, experience_required_options, \
        experience_required_months_options, job_location_options = prepare_options(cleaned_data)

    rome_code_selected = st.selectbox('Sélectionnez le code ROME :', ['Veuillez sélectionner une option'] + rome_data_unique['combined'].tolist(), index=0)
    rome_code_actual = rome_code_selected.split(' - ')[0] if rome_code_selected != "Veuillez sélectionner une option" else None

    contract_type = st.selectbox("Type de Contrat", ['Veuillez sélectionner une option'] + contract_type_options, index=0)
    experience_required = st.selectbox("Expérience Requise", ['Veuillez sélectionner une option'] + experience_required_options, index=0)
    experience_required_months = st.selectbox("Mois d'Expérience", ['Veuillez sélectionner une option'] + [str(m) for m in experience_required_months_options], index=0)
    job_location_code = st.selectbox("Code Postal", ['Veuillez sélectionner une option'] + job_location_options, index=0)


    if st.button("Prédire le Salaire"):
        # Validation des champs
        valid_rome = validate_field(rome_code_selected, error_message="Veuillez sélectionner un code ROME.")
        valid_experience = validate_field(experience_required_months, error_message="Veuillez indiquer les mois d'expérience.")
        valid_location = validate_field(job_location_code, error_message="Veuillez indiquer le code postal.")

        if valid_rome and valid_experience and valid_location:
            try:
                # Extraire le département des deux premiers chiffres du code postal
                job_location_department = str(job_location_code).zfill(2)[:2]

                # Préparer les données pour la prédiction
                input_data = pd.DataFrame({
                    'rome_code': [rome_code_actual],
                    'contract_type': [contract_type.split(' - ')[0]],  # Utiliser uniquement le code du contrat
                    'experience_required': [experience_required],
                    'experience_required_months': [float(experience_required_months)],  # Convertir explicitement en float
                    'departement': [job_location_department],
                    'code_postal': [str(job_location_code)]  # Assurer que le code postal est une chaîne
                })

                # Nettoyer et convertir les types si nécessaire
                input_data['rome_code'] = input_data['rome_code'].astype(str)
                input_data['contract_type'] = input_data['contract_type'].astype(str)
                input_data['experience_required'] = input_data['experience_required'].astype(str)
                input_data['experience_required_months'] = pd.to_numeric(input_data['experience_required_months'], errors='coerce').fillna(0).astype(float)
                input_data['departement'] = input_data['departement'].astype(str)
                input_data['code_postal'] = input_data['code_postal'].astype(str)

                # Faire la prédiction
                prediction = model.predict(input_data)
                st.success(f"Salaire Prévu : {prediction[0]:.2f} €")
            except ValueError as ve:
                st.error(f"Erreur de validation des données : {ve}")
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")


if __name__ == "__main__":
    main()
