import streamlit as st
import requests
import json
from tmdbv3api import TMDb, Movie
import streamlit.components.v1 as components
from streamlit.components.v1 import html

###
### Création des fonctions
###

# Fonction pour rechercher un film et obtenir ses informations
def rechercher_film(titre):
    try:
        film = Movie()
        resultats = film.search(titre)
        if resultats:
            res = resultats[0]  # Prendre le premier résultat
            film_id = res.id
            # Faire une requête pour obtenir les crédits (acteurs)
            credits_url = f'https://api.themoviedb.org/3/movie/{film_id}/credits?api_key={tmdb.api_key}&language=fr'
            credits_response = requests.get(credits_url)
            # Faire une requête pour obtenir les genres
            genres_url = f'https://api.themoviedb.org/3/movie/{film_id}?api_key={tmdb.api_key}&language=fr'
            details_response = requests.get(genres_url)
            acteurs = 'Non disponible'
            genres = 'Non disponible'
            duree = 'Non disponible'
            if credits_response.status_code == 200:
                credits_data = credits_response.json()
                acteurs = ', '.join([actor['name'] for actor in credits_data['cast'][:5]])  # Prendre les 5 premiers acteurs
            if details_response.status_code == 200:
                details_data = details_response.json()
                genres = ', '.join([genre['name'] for genre in details_data.get('genres', [])])  # Récupérer les genres
                runtime = details_data.get('runtime')  # Durée en minutes
                duree = convertir_duree(runtime) if runtime else "Non disponible"
            note = res.vote_average if res.vote_average is not None else 0
            note_arrondie = round(note, 1)  # Arrondi à 1 chiffre après la virgule
            return {
                'Titre': res.title,
                'Année': res.release_date,
                'Acteurs': acteurs,
                'Genres': genres,  # Ajout du genre
                'Note': note_arrondie,  # Utilisation de la note arrondie
                'Synopsis': res.overview,
                'Durée': duree,
                'Affiche': f"https://image.tmdb.org/t/p/w500{res.poster_path}" if res.poster_path else '',
                'Id': film_id,
                'GenresListe': details_data.get('genres', []),  # Retourner la liste des genres
                'BandeAnnonce': obtenir_bande_annonce(film_id)  # Ajouter la bande annonce
            }
        else:
            return None
    except Exception as e:
        st.error("Euhhh JB j'ai une question1")
        return None
    
# Fonction pour obtenir l'ID de la bande-annonce YouTube
def obtenir_bande_annonce(film_id):
    try:
        video_url = f'https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={tmdb.api_key}&language=fr'
        response = requests.get(video_url)
        if response.status_code == 200:
            videos = response.json().get('results', [])
            for video in videos:
                if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                    return video['key']  # Retourner l'ID de la vidéo YouTube
        return None  # Retourne None si aucune bande-annonce trouvée
    except Exception as e:
        st.error("Euhhh JB j'ai une question2")
        return None
    
def obtenir_suggestions_film(query):
    try:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={tmdb.api_key}&query={query}&language=fr"
        response = requests.get(search_url)
        if response.status_code == 200:
            results = response.json().get('results', [])
            suggestions = [result['title'] for result in results[:6]]  # Limiter à 6 suggestions
            return suggestions
        return []
    except Exception as e:
        st.error("Euhhh JB j'ai une question3")
        return []
    
# Fonction pour charger un fichier JSON
def charger_json(chemin):
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error("Erreur JSON : ",e)
        return []
    
# Chemins des fichiers JSON pour chaque genre
chemins_json = {
    'Action': "./Films_Genre_Action.json",
    'Adventure': "./Films_Genre_Adventure.json",
    'War': "./Films_Genre_War.json",
    'Western': "./Films_Genre_Western.json",
    'Thriller': "./Films_Genre_Thriller.json",
    'Sci-Fi': "./Films_Genre_Sci-Fi.json",
    'Romance': "./Films_Genre_Romance.json",
    'Mystery': "./Films_Genre_Mystery.json",
    'Music': "./Films_Genre_Music.json",
    'Horror': "./Films_Genre_Horror.json",
    'History': "./Films_Genre_History.json",
    'Film-Noir': "./Films_Genre_Film-Noir.json",
    'Fantasy': "./Films_Genre_Fantasy.json",
    'Family': "./Films_Genre_Family.json",
    'Drama': "./Films_Genre_Drama.json",
    'Crime': "./Films_Genre_Crime.json",
    'Comedy': "./Films_Genre_Comedy.json",
    'Biography': "./Films_Genre_Biography.json",
    'Animation': "./Films_Genre_Animation.json",
    'ALL': "./Films_ALL.json"  # Ajout du fichier Films_ALL.json
}

# Fonction pour obtenir les recommandations d'un film en fonction de son genre
def get_recommendations_par_genre(genre, id_film):
    recommendations = []
    try:
        if genre in chemins_json:
            genre_json = charger_json(chemins_json[genre])
            for item in genre_json:
                if item['id_film'] == id_film:
                    for i in range(1, 7):  # Pour les 5 recommandations possibles
                        reco_id = item.get(f'id_reco{i}')
                        if reco_id:
                            recommendations.append(reco_id)
        return recommendations
    except Exception as e:
        # Afficher l'erreur dans Streamlit
        st.error("Erreur reco_genre : ",e)
        return []
    
# Fonction pour obtenir des recommandations globales depuis Films_ALL.json
def get_recommendations_globale(id_film):
    recommendations = []
    try:
        all_json = charger_json(chemins_json['ALL'])  # Charger le fichier global
        for item in all_json:
            if item['id_film'] == id_film:
                for i in range(1, 6):  # Pour les 5 recommandations possibles
                    reco_id = item.get(f'id_reco{i}')
                    if reco_id:
                        recommendations.append(reco_id)
        return recommendations
    except Exception as e:
        st.error("Erreur reco_globale : ",e)
        return []

###
### Chargement de la page
###

st.set_page_config(page_title="Application de recommandation de films",layout="wide")
st.logo("https://baptistedrapeau.wordpress.com/wp-content/uploads/2019/02/logo-cave-c3a0-film-rond-blanc-noir.png", size="large", link=None, icon_image=None)

# Haut de la page
st.markdown('<a id="top"></a>', unsafe_allow_html=True)  # Marqueur pour retourner en haut de la page

tab1, tab2 = st.tabs(["|   Recommandations de film   |", "|   KPIs sur la Creuse et le cinéma   |"])

with tab1:
    # Initialiser l'objet TMDb et définir la clé API
    tmdb = TMDb()
    tmdb.api_key = '5705ee01faebcd87a6faed03885adae0'
    tmdb.language = 'fr'
    def convertir_duree(minutes):
        if not isinstance(minutes, int) or minutes <= 0:
            return "Non disponible"
        heures = minutes // 60
        reste_minutes = minutes % 60
        return f"{heures}h {reste_minutes}min"
   
    # Interface Streamlit
    st.title("Trouvons ensemble le  film qui va illuminer votre soirée !")
    # Initialiser la variable `search_input` dans `session_state` si elle n'existe pas
    if 'search_input' not in st.session_state:
        st.session_state.search_input = ''
        st.rerun()
    # Afficher la barre de recherche
    choixfilm = st.text_input("Recherche : ", value=st.session_state.search_input)
    # Mettre à jour la valeur de `search_input` à chaque modification de la barre de recherche
    if choixfilm != st.session_state.search_input:
        st.session_state.search_input = choixfilm
        st.rerun()
    if choixfilm:
        suggestions = obtenir_suggestions_film(choixfilm)
        if suggestions:
            selected_film = st.selectbox("Titre similaire :", suggestions)
            if selected_film:
                film_info = rechercher_film(selected_film)
                if film_info:
                    # Affichage de l'affiche du film et des informations
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if film_info['Affiche']:
                            st.image(film_info['Affiche'])
                    with col2:
                        st.write(f"**Titre :** {film_info['Titre']}")
                        st.write(f"**Année :** {film_info['Année']}")
                        st.write(f"**Acteurs :** {film_info['Acteurs']}")
                        st.write(f"**Genres :** {film_info['Genres']}")
                        st.write(f"**Note :** {film_info['Note']}")
                        st.write(f"**Synopsis :** {film_info['Synopsis']}")
                        st.write(f"**Durée :** {film_info['Durée']}")
                    # Afficher la bande-annonce YouTube si disponible
                    bande_annonce = film_info['BandeAnnonce']
                    if bande_annonce:
                        st.markdown(f'<iframe width="100%" height="500" src="https://www.youtube.com/embed/{bande_annonce}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                    # Obtenir le genre du film et charger les recommandations
                    genres = [genre['name'] for genre in film_info['GenresListe']]
                    recommendations = []
                    for genre in genres:
                        recommendations.extend(get_recommendations_par_genre(genre, film_info['Id']))
                    # Ajouter les recommandations globales
                    recommendations.extend(get_recommendations_globale(film_info['Id']))
                    # Filtrer les films recommandés pour éviter les doublons
                    recommendations = list(set(recommendations))  # Supprimer les doublons
                    recommendations = recommendations[:5]  # Limiter à 5 films
                    # Afficher les recommandations
                    # Afficher les recommandations sous forme d'affiches avec titres seulement
                    if recommendations:
                        st.subheader("**Vous avez apprécié ? Voici des recommandations qui pourraient vous plaire !**")
                        col1, col2, col3, col4, col5 = st.columns(5)  # Créer 5 colonnes pour les affiches
                        columns = [col1, col2, col3, col4, col5]
                        for i, reco_id in enumerate(recommendations):
                            reco_film = Movie()
                            reco_film_info = reco_film.details(reco_id)
                            if reco_film_info:
                                with columns[i]:  # Affichage dans les colonnes créées
                                    if reco_film_info.poster_path:
                                        st.image(f"https://image.tmdb.org/t/p/w500{reco_film_info.poster_path}", use_container_width=True)  # Affiche la même taille que la colonne de texte
                                    st.write(f"**{reco_film_info.title}**")  # Affichage du titre des films recommandés
                                    # Ajouter un bouton sous chaque affiche
                                    if st.button(f"Plus de détails...", key=reco_film_info.id):
                                            st.session_state.search_input = reco_film_info.title  # Remplacer le titre actuel par celui de la reco
                                            st.rerun()  # Recharger la page pour afficher le film sélectionné dans la barre de recherche
 
            # Retourner en haut de la page
            st.markdown('<a href="#top">Retour en haut de la page</a>', unsafe_allow_html=True)

with tab2:
    st.title("Visualisez votre tableau de bord à partir des données :")
    tab21, tab22, tab23 , tab24 = st.tabs(["|   INSEE   |", "|   CNC   |", "|   Data Gouv   |", "|   IMdB   |"])
    with tab21:
        # embed streamlit docs in a streamlit app - INSEE
        components.iframe("https://app.powerbi.com/view?r=eyJrIjoiYjdlNWZiMmEtMmJmMy00ZjNjLWJjYWEtNmRkZDIxYTY5Mjc1IiwidCI6ImYyODRkYTU4LWMwOTMtNGZiOS1hM2NiLTAyNDNjM2EwMTRhYyJ9", width=1024, height=804)

    with tab22:
        # embed streamlit docs in a streamlit app - CNC
        components.iframe("https://app.powerbi.com/view?r=eyJrIjoiYzc4MzMxNzUtOWY5Ny00ZmE2LTlkYzMtNGY2YTkzZTdkN2QyIiwidCI6ImYyODRkYTU4LWMwOTMtNGZiOS1hM2NiLTAyNDNjM2EwMTRhYyJ9", width=1024, height=804)

    with tab23:
        # embed streamlit docs in a streamlit app - DataGouv
        components.iframe("https://app.powerbi.com/view?r=eyJrIjoiYjIwMDdjN2MtY2NlNy00NmNlLWFlZjAtMWIxMTRlMzcxMGVkIiwidCI6ImYyODRkYTU4LWMwOTMtNGZiOS1hM2NiLTAyNDNjM2EwMTRhYyJ9", width=1024, height=804)
    with tab24:
        # embed streamlit docs in a streamlit app - IMDB
        components.iframe("https://app.powerbi.com/view?r=eyJrIjoiNzdiYTQ5OTMtMGIxNy00NTk5LTkzOWItNzEwYmJhNGVmZmZmIiwidCI6ImYyODRkYTU4LWMwOTMtNGZiOS1hM2NiLTAyNDNjM2EwMTRhYyJ9", width=1024, height=804)


css = '''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:2rem;
    }
</style>
'''

st.markdown(css, unsafe_allow_html=True)