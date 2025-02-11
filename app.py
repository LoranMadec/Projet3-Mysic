import streamlit as st
import pandas as pd
import gdown
import json
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import time
import numpy as np
import requests

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import google.generativeai as genai
import os
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title = "Application de recommandations de musique", page_icon = ":notes_de_musique:", layout = "wide")

GOOGLE_API_KEY='AIzaSyBQLR4y1s7SycCHfBLbJSggFJaRGMo2Zgo'
genai.configure(api_key=GOOGLE_API_KEY)

# Clé pour Riffusion
user = 'laurent.lolo.madec@gmail.com'
pwd='H3c+Y8t*75<^)CD'

############################################################################################################
### Définition des fonctions################################################################################
############################################################################################################
# Charger les données avec mise en cache
@st.cache_data

# Fonction pour charger les données à partir d'un fichier CSV
def load_data():
    df_original = pd.read_csv("df_streamlit.csv")
    suggestions = df_original['TitreIA'].tolist()
    df_result = df_original[["titre", "artists", "release_date"]]
    df = df_original[["id", "titre", "popularity", "artists", "release_date", "decennie", "durée", "genres", "TitreIA"]]
    # renvoi la liste des genres classés par ordre alphabétique
    list_genres = sorted(df['genres'].str.split(', ').explode().unique())
    return df, df_result, suggestions, list_genres

# Fonction pour afficher les tracks en fonction des filtres
def obtenir_track(query,genre,decennie):
    try:
        if query != 'all':
            if genre == 'all':
                if decennie == 'all':
                    results = df_tracks[df_tracks['TitreIA'].str.contains(query, case=False, na=False)]
                else:
                    results = df_tracks[(df_tracks['TitreIA'].str.contains(query, case=False, na=False)) & (df_tracks['decennie'] == decennie)]
            else:
                if decennie == 'all':
                    results = df_tracks[(df_tracks['TitreIA'].str.contains(query, case=False, na=False)) & (df_tracks['genres'].str.contains(genre, case=False, na=False))]
                else:
                    results = df_tracks[(df_tracks['TitreIA'].str.contains(query, case=False, na=False)) & (df_tracks['genres'].str.contains(genre, case=False, na=False)) & (df_tracks['decennie'] == decennie)]
        else:
            if genre == 'all':
                if decennie != 'all':
                    results = df_tracks[df_tracks['decennie'] == decennie]
            else:
                if decennie == 'all':
                    results = df_tracks[df_tracks['genres'].str.contains(genre, case=False, na=False)]
                else:
                    results = df_tracks[(df_tracks['genres'].str.contains(genre, case=False, na=False)) & (df_tracks['decennie'] == decennie)]

        return results
    except Exception as e:
        st.error("Euhhh JB j'ai une question3")
        return []

# Fonction pour obtenir images album et artists + extrait audio d'une musique à partir de l'API Deezer
def get_track_preview(artist, track):
    base_url = "https://api.deezer.com/search"
    params = {
        "q": f"artist:'{artist}' track:'{track}'",
        "limit": 1  # Limiter la recherche à une seule correspondance
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        # Check if the 'data' key exists and contains any tracks
        if data.get('data') and len(data['data']) > 0:
            track_info = data['data'][0]
            preview_url = track_info.get('preview')
            link_track = track_info.get('link')
            # Access artist and album information from the track data
            artist_picture = track_info.get('artist', {}).get('picture_medium')
            album_picture = track_info.get('album', {}).get('cover_medium')
            album_titre = track_info.get('album', {}).get('title')
            if preview_url:
                return preview_url, link_track, artist_picture, album_picture, album_titre
            else:
                return None, None, None, None, None
        else:
            return None, None, None, None, None
    else:
        return None, None, None, None, None

# Fonction pour charger un fichier JSON
def charger_json(chemin):
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du JSON {chemin}: {str(e)}")  # ✅ Correction ici
        return []

# Chemins des fichiers JSON pour chaque genre et par décennie
chemins_json = {
    'Classical': "./Classical.json",
    'Country': "./Country.json",
    'Electronic-Dance': "./Electronic-Dance.json",
    'Hip-Hop/Rap': "./Hip-Hop-Rap.json",
    'Jazz': "./Jazz.json",
    'Latin': "./Latin.json",
    'Pop': "./Pop.json",
    'RB-Soul': "./RB-Soul.json",
    'Reggae': "./Reggae.json",
    'Rock': "./Rock.json",
    '1920': "./Musicalite_1920.json",
    '1930': "./Musicalite_1930.json",
    '1940': "./Musicalite_1940.json",
    '1950': "./Musicalite_1950.json",
    '1960': "./Musicalite_1960.json",
    '1970': "./Musicalite_1970.json",
    '1980': "./Musicalite_1980.json",
    '1990': "./Musicalite_1990.json",
    '2000': "./Musicalite_2000.json",
    '2010': "./Musicalite_2010.json",
    '2020': "./Musicalite_2020.json"
}

# Fonction pour obtenir les recommandations d'un track en fonction de son genre
def get_recommendations_par_genre(genre, id_track):
    recommendations = []
    try:
        if genre in chemins_json:
            genre_json = charger_json(chemins_json[genre])
            for item in genre_json:
                if item['id_track'] == id_track:
                    for i in range(1, 4):  # Pour les 3 recommandations possibles
                        reco_id = item.get(f'id_reco{i}')
                        if reco_id:
                            recommendations.append(reco_id)
        return recommendations
    except Exception as e:
        st.error(f"⚠️ Erreur reco_genre : {e}")  # ✅ Correction ici
        return []


# Fonction pour obtenir les recommandations d'un track en fonction de sa décennie
def get_recommendations_par_decennie(decennie, id_track):
    recommendations = []
    try:
        decennie_str = str(decennie)
        if decennie_str in chemins_json:
            decennie_json = charger_json(chemins_json[decennie_str])
            for item in decennie_json:
                if item.get('id_track') == id_track:  # ✅ Utiliser `.get()` pour éviter KeyError
                    for i in range(1, 4):  # ✅ Vérifier les 3 recommandations possibles
                        reco_id = item.get(f'id_reco{i}')
                        if reco_id:
                            recommendations.append(reco_id)
        return recommendations
    except Exception as e:
        st.error(f"⚠️ Erreur reco_decennie : {str(e)}")  # ✅ Correction ici
        return []


# Fonction pour rechercher une chanson et obtenir ses informations
def rechercher_track(id_track):
    try:
        resultats = df_tracks[df_tracks['id'] == id_track]
        if not resultats.empty:
            res = resultats.iloc[0]  # Prendre le premier résultat
            return {
                'Titre': res.titre,
                'TitreIA': res.TitreIA,
                'Artiste': res.artists,
                'Décennie': res.decennie,
                'DateSortie': res.release_date,
                'Genre': res.genres,
                'NotePopularité': res.popularity,
                'Durée': res.durée,
                'Id': res.id
            }
        else:
            return None
    except Exception as e:
        st.error("Euhhh JB j'ai une question1")
        return None


# Fonction pour générer une musique à partir d'un prompt sur Riffusion

def generer_musique(type,param):

    # Création des dictionaires des urls et pistes audio par genre
    dic_genre = {"Rock":"https://www.riffusion.com/riff/2ff9658a-efb6-4223-8470-3fe304b69556",
                 "Pop":"https://www.riffusion.com/riff/4c7279a5-c90e-47cc-847d-91f8e0b10832",
                 "Reggae":"https://www.riffusion.com/riff/5efcb6a3-750c-4c36-80dd-8fc2829192bd",
                 "Latin":"https://www.riffusion.com/riff/081362aa-879d-4a06-b9f4-f163edabca02",
                 "Jazz":"https://www.riffusion.com/riff/3fa868ea-242f-47fc-b99a-57794f890b67",
                 "Electronic-Dance":"https://www.riffusion.com/riff/1473cf2a-8bf8-45c3-a4bd-61408a19804f",
                 "Hip-Hop/Rap":"https://www.riffusion.com/riff/a84674e7-91c6-4327-b80f-485fd389fc04",
                 "Country":"https://www.riffusion.com/riff/b75dd4f6-c5b2-4c86-8cdc-b3f434e06dee",
                 "Classical":"https://www.riffusion.com/riff/6d52f5f4-491a-4469-9962-e7fd85877b58",
                 "RB-Soul":"https://www.riffusion.com/riff/f44d025c-982d-41de-a93e-38ddb3f77403"}

    dic_genre_audio = {"Rock":"./Audio/Guardian's Flame.m4a",
                        "Pop":"./Audio/Just Like Old Times.m4a",
                        "Reggae":"./Audio/Two Streets, One Truth.m4a",
                        "Latin":"./Audio/Baila Conmigo Esta Noche.m4a",
                        "Jazz":"./Audio/Empty Table Blues.m4a",
                        "Electronic-Dance":"./Audio/Tonight We Rise.m4a",
                        "Hip-Hop/Rap":"./Audio/Night Shift Knowledge.m4a",
                        "Country":"./Audio/That Screen Door's Been Quiet.m4a",
                        "Classical":"./Audio/The Gardener's Farewell.m4a",
                        "RB-Soul":"./Audio/Let The Storm Roll.m4a"}

    # Création du dictionaire des urls par décennie
    dic_decennie = {"1920":"https://www.riffusion.com/riff/47293efb-385e-4051-b815-2e5255a3a1d8",
                    "1930":"https://www.riffusion.com/riff/8c9eb6ea-c2ac-4b13-8b1a-ef7c7bbd4597",
                    "1940":"https://www.riffusion.com/riff/34ded871-1b8b-4e3d-bfc3-1b9fbb221e74",
                    "1950":"https://www.riffusion.com/riff/39a70308-f3fa-46f1-8dc3-8b8850129634",
                    "1960":"https://www.riffusion.com/riff/31542784-0e1f-4531-acf8-df282232def5",
                    "1970":"https://www.riffusion.com/riff/3a37c6b9-f811-4502-8b8e-e1e230ad2b2d",
                    "1980":"https://www.riffusion.com/riff/ea2b1315-fd39-458b-8181-939b9da48790",
                    "1990":"https://www.riffusion.com/riff/3b88a9f3-f7a8-4f8c-b0be-c94fc05e3487",
                    "2000":"https://www.riffusion.com/riff/3bfa535b-1f34-4ce2-ab39-47c9b93cb80b",
                    "2010":"https://www.riffusion.com/riff/f02b287e-2f7a-4fec-afe5-032232b7d750",
                    "2020":"https://www.riffusion.com/riff/35258c2a-1a72-4d3e-b121-9e9cb9910a6b"}

    dic_decennie_audio = {"1920":"./Audio/Borrowed Youth Blues.m4a",
                            "1930":"./Audio/Watching You Dance.m4a",
                            "1940":"./Audio/Coffee Stains.m4a",
                            "1950":"./Audio/Café Des Amoureux.m4a",
                            "1960":"./Audio/Dancing in the Grass.m4a",
                            "1970":"./Audio/Dancing Through The Dark.m4a",
                            "1980":"./Audio/Radio Time Machine.m4a",
                            "1990":"./Audio/Screen Life Lies.m4a",
                            "2000":"./Audio/Wide Open Spaces.m4a",
                            "2010":"./Audio/Dancing in Disconnect.m4a",
                            "2020":"./Audio/Dancing Through Screens.m4a"}
    
    if type == "genre":
        lien = dic_genre[param]
        audio = dic_genre_audio[param]
    elif type == "decennie":
        lien = dic_decennie[param]
        audio = dic_decennie_audio[param]
    else:
        lien = "Aucune génération possible"
        audio = "Aucune génération possible"     

    return lien,audio

#########################################################################################
#############################          CSS   ############################################
#########################################################################################

#gère taille image logo
st.markdown("""
<style>
img[data-testid="stLogo"] {height: 4rem;}
</style>""", unsafe_allow_html=True)


# Appliquer le thème via st.markdown avec du CSS
st.markdown(
    """
    <style>
        :root {
            --primary-color: #3393F1;
            --background-color: #FFFFFF;
            --secondary-background-color: #3393F1;
            --text-color: #000000;
            --font-family: 'Source Sans Pro';
        }

        html, body {
            background-color: var(--background-color) !important;
            color: 000000 !important;
            font-family: var(--font-family) !important;
            font-size: 18px !important;
        }

        .stButton > button {
            border: 1px solid red !important; /* ✅ Bordure blanche pour meilleure visibilité */
            font-weight: bold !important; /* ✅ Texte en gras */
            border-radius: 5px !important; /* ✅ Arrondi des bords pour un meilleur design */
            }

        /* ✅ Change la couleur du bouton au survol */
        .stButton > button:hover {
            background-color: #D00D0D !important; /* ✅ Rouge plus foncé au survol */
            color: white !important;
            }

        .stSidebar {
            background-color: var(--secondary-background-color) !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
        /* Augmente l'espacement entre les onglets */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }

        /* Style général des onglets */
        .stTabs [data-baseweb="tab"] {
            height: 60px;  /* ✅ Augmente la hauteur */
            white-space: pre-wrap;
            background-color: #F20F0F !important;  /* ✅ Rouge forcé */
            border-radius: 8px 8px 0 0;  /* ✅ Bords arrondis */
            padding: 15px 30px;
            color: white !important; /* ✅ Texte en blanc */
            font-size: 48px !important;  /* ✅ Augmente la taille de la police */
            font-weight: bold !important; /* ✅ Texte en gras */
            text-align: center !important;
        }

        /* Style de l'onglet actif */
        .stTabs [aria-selected="true"] {
            background-color: #D00D0D !important; /* ✅ Rouge légèrement plus foncé */
            color: white !important; /* ✅ Texte blanc */
            font-size: 26px !important; /* ✅ Texte un peu plus grand pour l'onglet actif */
            border-bottom: 4px solid white !important;  /* ✅ Ajoute une séparation visuelle */
        }

        /* ✅ Assure que le texte reste blanc dans tous les cas */
        .stTabs [data-baseweb="tab"] * {
            color: white !important;
        }

    </style>
""", unsafe_allow_html=True)


#bannière :
# Convertir l'image en base64 pour l'afficher en HTML
def get_base64_of_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
# Charger l'image
image_base64 = get_base64_of_image("./image/banniere.png")
# Code HTML/CSS pour afficher la bannière
custom_html = f"""
<div class="banner">
    <img src="data:image/png;base64,{image_base64}" alt="Bannière">
</div>
<style>
    .banner {{
        width: 100%;
        height: 200px;
        overflow: hidden;
        border-radius: 5px !important; /* ✅ Arrondi des bords pour un meilleur design */
    }}
    .banner img {{
        width: 100%;
        object-fit: cover;
    }}
</style>
"""
# Afficher le HTML pour la bannière
st.markdown(custom_html, unsafe_allow_html=True)

# Logo
st.logo("./image/Logo.png", size="large", link=None, icon_image=None)

############################################################################################
############################################################################################
############################################################################################

# Haut de la page
# Removing whitespace from the top of the page
st.markdown("""
<style>
.css-18e3th9 { padding-top: 0rem; padding-bottom: 10rem; padding-left: 5rem; padding-right: 5rem; }
.css-1d391kg { padding-top: 3.5rem; padding-right: 1rem; padding-bottom: 3.5rem; padding-left: 1rem; }
</style>""", unsafe_allow_html=True)


# Haut de la page
st.markdown('<a id="top"></a>', unsafe_allow_html=True)  # Marqueur pour retourner en haut de la page

url_image_album_vide = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/eb777e7a-7d3c-487e-865a-fc83920564a1/d7kpm65-437b2b46-06cd-4a86-9041-cc8c3737c6f0.jpg/v1/fill/w_800,h_800,q_75,strp/no_album_art__no_cover___placeholder_picture_by_cmdrobot_d7kpm65-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9ODAwIiwicGF0aCI6IlwvZlwvZWI3NzdlN2EtN2QzYy00ODdlLTg2NWEtZmM4MzkyMDU2NGExXC9kN2twbTY1LTQzN2IyYjQ2LTA2Y2QtNGE4Ni05MDQxLWNjOGMzNzM3YzZmMC5qcGciLCJ3aWR0aCI6Ijw9ODAwIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmltYWdlLm9wZXJhdGlvbnMiXX0.8yjX5CrFjxVH06LB59TpJLu6doZb0wz8fGQq4tM64mg"

tab1, tab2 = st.tabs(["|   MyZic IA   |", "|   KPIs sur MyZic   |"])

# Importer les données
df_tracks, df_result, suggestions, list_genres = load_data()

with tab1:
    col1, col2 = st.columns([1, 3],border=True)
    with col1:
        st.subheader("Filtres")
        # Recherche d'une chanson
        # Barre de recherche
        if 'search_input' not in st.session_state:
            st.session_state.search_input = ''
            st.rerun()
        # Afficher la barre de recherche
        choixtrack = st.text_input("Recherche une chanson ou un artiste : ", value=st.session_state.search_input)
        # Choix du genre avec afficher le texte 'choisir un genre' dans la liste déroulante
        choixgenre = st.selectbox("Choisis un genre :",list_genres, placeholder="dans cette liste", index=None)

        # choix décennie triée par ordre décroissant
        choixdecennie = st.selectbox("Choisis une décennie :", sorted(df_tracks['decennie'].unique(), reverse=True), placeholder="dans cette liste", index=None)

    with col2:
        stop=0
        if choixtrack:
            if choixgenre:
                results = obtenir_track(choixtrack,choixgenre,'all')
                if choixdecennie:
                    results = obtenir_track(choixtrack,choixgenre,choixdecennie)
            elif choixdecennie:
                results = obtenir_track(choixtrack,'all',choixdecennie)
            else:
                results = obtenir_track(choixtrack,'all','all')
        else:
            if choixgenre:
                results = obtenir_track('all',choixgenre,'all')
                if choixdecennie:
                    results = obtenir_track('all',choixgenre,choixdecennie)
            elif choixdecennie:
                results = obtenir_track('all','all',choixdecennie)
            else:
                st.info("Recherche une chanson ou un artiste et laisse notre IA te surprendre !")
                stop=1

        if not stop:

            # Trier les résultats par popularité
            results = results.sort_values(by='popularity', ascending=False)

            # Afficher les résultats dans un DataFrame interactif avec la possibilité de sélectionner une ligne via la première colonne
            st.info("Sélectionne une chanson et laisse notre IA te surprendre !")
            edited_df = st.dataframe(results[['id','popularity','artists','titre','release_date']],
                        use_container_width=True, hide_index=True,
                        column_config={
                                        "id": None,
                                        "popularity": None,
                                        "artists": "Artiste",
                                        "titre": "Titre",
                                        "release_date": "Date de sortie"},
                        on_select="rerun",
                        height=350,
                        selection_mode="single-row"
                        )
            # Afficher d'id de la ligne sélectionnée
            selection = edited_df.selection.rows

            if selection:
                id_selected = results.iloc[selection[0]]['id']

                if not results.empty:
                    selected_track_id = id_selected
                    TitreIA_Liste_Genre = []
                    TitreIA_Liste_Dec = []
                    if selected_track_id:
                        track_info = rechercher_track(selected_track_id)
                        if track_info:
                            # Ajout du titre IA dans la liste TitreIA_Liste
                            TitreIA_Liste_Genre.append(track_info['TitreIA'])
                            TitreIA_Liste_Dec.append(track_info['TitreIA'])
                            artist_name = track_info['Artiste']
                            track_name = track_info['Titre']
                            preview, link, artist_picture, album_picture, album_titre = get_track_preview(artist_name, track_name)

                            # Affichage du titre de la chanson et de l'album
                            st.write(f"**{album_titre} - {track_info['Titre']}**")
                            # Affichage de l'affiche de la chanson et de ses informations
                            col1, col2 = st.columns([1, 2])
                            with col1:
                                if album_picture:
                                    st.image(album_picture,)
                                else:
                                    st.image(url_image_album_vide, width=250)

                                if preview:
                                    st.audio(preview)
                                else:
                                    st.audio('https://audio.mp3')

                            with col2:
                                st.write(f"🎤 **Artiste :** {track_info['Artiste']}")
                                st.write(f"📅 **Date de Sortie :** {track_info['DateSortie']}")
                                st.write(f"🎵 **Genres :** {track_info['Genre']}")
                                st.write(f"⏳ **Durée :** {track_info['Durée']}")
                                st.write(f"⭐ **Note de popularité :** {track_info['NotePopularité']}")

                            # Obtenir le genre de la chanson et charger les recommandations du même genre
                            # 1er genre avant la , si plusieurs genres
                            if ',' in track_info['Genre']:
                                genres = track_info['Genre'].split(',')[0]
                            else:
                                genres = track_info['Genre']

                            recommendationsgenre = []
                            recommendationsgenre.extend(get_recommendations_par_genre(genres, selected_track_id))
                            # Filtrer les tracks recommandés pour éviter les doublons
                            recommendationsgenre = list(set(recommendationsgenre))  # Supprimer les doublons
                            recommendationsgenre = recommendationsgenre[:3]  # Limiter à 3 tracks
                            # Afficher les recommandations
                            if recommendationsgenre:
                                if st.button(f"**Check nos recommandations ''{genres}'' !**", use_container_width=True, type="primary"):
                                    col1, col2, col3 = st.columns(3)  # Créer 3 colonnes pour les titres
                                    columns = [col1, col2, col3]
                                    for i, reco_id in enumerate(recommendationsgenre):
                                        reco_track_info = rechercher_track(reco_id)
                                        if reco_track_info:
                                            # Ajout du titre IA dans la liste TitreIA_Liste
                                            TitreIA_Liste_Genre.append(reco_track_info['TitreIA'])

                                            with columns[i]:  # Affichage dans les colonnes créées
                                                artist_name = reco_track_info['Artiste']
                                                track_name = reco_track_info['Titre']
                                                preview, link, artist_picture, album_picture, album_titre = get_track_preview(artist_name, track_name)

                                                if album_picture:
                                                    st.image(album_picture)
                                                else:
                                                    st.image(url_image_album_vide, width=250)
                                                if preview:
                                                    st.audio(preview)
                                                else:
                                                    st.audio('https://audio.mp3')
                                                st.write(f"{reco_track_info['TitreIA']}")

                            # Ajouter un bouton pour générer la music IA
                            if st.button(f"Les recos ''{genres}'' de notre IA", key=f"generate_{selected_track_id}_IA", use_container_width=True):

                                # Création du modèle de Chatbot musical
                                model = genai.GenerativeModel('gemini-2.0-flash-exp')

                                # Création du prompt système
                                system_prompt = """
                                Tu es un spécialiste de la musique. Tu donnes des réponses précises en les replaçant dans le contexte musical.
                                """

                                #Initialisation de l'historique avec le prompt système
                                chat = model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}])

                                # Envoi du message au chatbot pour générer une note synthétique en anglais de moins de 200 caractères pour générer dans une autre IA une chanson à partir de la liste des chansons recommandées présentes dans TitreIA_Liste
                                message = "Bonjour, peux-tu me proposer 3 chansons du même genre " + genres + "que la chanson suivante : " + track_info['TitreIA'] + " ?"
                                response = chat.send_message(message).text
                                message2 = "Peux-tu m'afficher ces 3 chansons dans un dictionnaire JSON que tu mettra entre [] et uniquement ce dictionnaire JSON sans explication avec les index nommés titre et artiste pour chaque chaque chanson ?"
                                note = chat.send_message(message2).text

                                # Recupération du dictionnaire de note qui est présent entre [] et le transformer en dictionnaire, avec suppression des [ et ] pour obtenir un dictionnaire
                                dict_reco = note[note.find('['):note.find(']')+1]

                                # Transformation de dict_reco en dictionnaire
                                dict_reco = json.loads(dict_reco)

                                col1, col2, col3 = st.columns(3)  # Créer 3 colonnes pour les titres
                                columns = [col1, col2, col3]

                                # Pour chaque élement de dict_reco, appel de rechercher_track
                                for i in range(0,3):
                                    titre = dict_reco[i]['titre']
                                    artiste = dict_reco[i]['artiste']

                                    with columns[i]:  # Affichage dans les colonnes créées
                                        preview, link, artist_picture, album_picture, album_titre = get_track_preview(artiste, titre)

                                        if album_picture:
                                            st.image(album_picture)
                                        else:
                                            st.image(url_image_album_vide, width=250)
                                        if preview:
                                            st.audio(preview)
                                        else:
                                            st.audio('https://audio.mp3')
                                        st.write(f"{dict_reco[i]['titre']} - {dict_reco[i]['artiste']}")


                                st.write("**Vous trouverez ci-dessous la description du choix de notre IA !**")
                                # Afficher tout le texte response après le premier caractère ':' trouvé
                                st.write(response[response.find(':')+1:])


                            # Ajouter un bouton pour générer la music IA
                            if st.button(f"Laisses notre IA générer ta chanson ''{genres}''", key=f"generate_{selected_track_id}{genres}", use_container_width=True):
                                for i, reco_id in enumerate(recommendationsgenre):
                                    reco_track_info = rechercher_track(reco_id)
                                    if reco_track_info:
                                        # Ajout du titre IA dans la liste TitreIA_Liste
                                        TitreIA_Liste_Genre.append(reco_track_info['TitreIA'])

                                # Création du modèle de Chatbot musical
                                model = genai.GenerativeModel('gemini-2.0-flash-exp')

                                # Création du prompt système
                                system_prompt = """
                                Tu es un spécialiste de la musique. Tu donnes des réponses précises en les replaçant dans le contexte musical.
                                """

                                #Initialisation de l'historique avec le prompt système
                                chat = model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}])

                                # Envoi du message au chatbot pour générer une note synthétique en anglais de moins de 200 caractères pour générer dans une autre IA une chanson à partir de la liste des chansons recommandées présentes dans TitreIA_Liste
                                message = "Bonjour, peux-tu générer une phrase synthétique entre crochets de moins de 250 caractères en anglais, ainsi que l'explication en français de la constitution de cette phrase pour générer dans une autre IA une chanson à partir des 4 chansons suivantes : " + ', '.join(TitreIA_Liste_Genre) + " sans citer ces chansons dans la phrase synthétique, mais en insistant sur les caratéristiques du genre"
                                response = chat.send_message(message).text

                                note = response[response.find('['):response.find(']')+1]
                                note = note.replace('"[','')
                                note = note.replace(']"','')
                                note = note.replace('[','')
                                note = note.replace(']','')

                                # Si note > 250 caractères, on complète pour que le positionnement de la souris soit OK
                                if len(note) < 250:
                                    if len(note) < 150:
                                        note = note + ' ' * (450 - len(note)) + 'end'
                                    else:
                                        note = note + ' ' * (300 - len(note)) + 'end'

                                response = response.replace('"[','')
                                response = response.replace(']"','')
                                response = response.replace('[','')
                                response = response.replace(']','')

                                # Afficher tout le texte response après le premier caractère ':' trouvé
                                st.write("**Avant d'écouter votre chanson, vous trouverez ci-dessous la description de celle-ci**")
                                st.write(response)

                                with st.spinner("Génération de la musique via Webscrapping en cours..."):
                                    time.sleep(10)

                                with st.spinner("Téléchargement en cours..."):
                                    time.sleep(3)

                                lien,audio = generer_musique("genre",genres)

                                st.write(f"**Votre musique générée via Riffusion :**")
                                st.audio(f"{audio}")
                                st.write(f"{lien}")


                            # Obtenir la decennie de la chanson et charger les recommandations de cette decennie
                            decennie = track_info['Décennie']
                            recommendationsdec = []
                            recommendationsdec.extend(get_recommendations_par_decennie(decennie, selected_track_id))

                            # Filtrer les tracks recommandés pour éviter les doublons
                            recommendationsdec = list(set(recommendationsdec))  # Supprimer les doublons
                            recommendationsdec = recommendationsdec[:3]  # Limiter à 3 tracks

                            # Afficher les recommandations
                            if recommendationsdec:
                                if st.button(f"**Check nos recommandations de {decennie} !**",use_container_width=True, type="primary"):
                                    col1, col2, col3 = st.columns(3)  # Créer 3 colonnes pour les titres
                                    columns = [col1, col2, col3]
                                    for i, reco_id in enumerate(recommendationsdec):
                                        reco_track_info = rechercher_track(reco_id)

                                        if reco_track_info:
                                            # Ajout du titre IA dans la liste TitreIA_Liste
                                            TitreIA_Liste_Dec.append(reco_track_info['TitreIA'])

                                            with columns[i]:  # Affichage dans les colonnes créées
                                                artist_name = reco_track_info['Artiste']
                                                track_name = reco_track_info['Titre']
                                                preview, link, artist_picture, album_picture, album_titre = get_track_preview(artist_name, track_name)

                                                if album_picture:
                                                    st.image(album_picture)
                                                else:
                                                    st.image(url_image_album_vide, width=250)
                                                if preview:
                                                    st.audio(preview)
                                                else:
                                                    st.audio('https://audio.mp3')
                                                st.write(f"{reco_track_info['TitreIA']}")

                            # Ajouter un bouton pour générer la music IA
                            if st.button(f"Les recos {decennie} de notre IA", key=f"generate_{selected_track_id}_dec_IA", use_container_width=True):

                                # Création du modèle de Chatbot musical
                                model = genai.GenerativeModel('gemini-2.0-flash-exp')

                                # Création du prompt système
                                system_prompt = """
                                Tu es un spécialiste de la musique. Tu donnes des réponses précises en les replaçant dans le contexte musical.
                                """

                                #Initialisation de l'historique avec le prompt système
                                chat = model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}])

                                # Convertir decennie en chaîne de caractères
                                decennie_str = str(decennie)

                                # Envoi du message au chatbot pour générer une note synthétique en anglais de moins de 200 caractères pour générer dans une autre IA une chanson à partir de la liste des chansons recommandées présentes dans TitreIA_Liste
                                message = "Bonjour, peux-tu me proposer 3 chansons de la même décennie " + decennie_str + " et avec les mêmes caractéristiques musicales que la chanson suivante : " + track_info['TitreIA'] + " ?"
                                response = chat.send_message(message).text
                                message2 = "Peux-tu m'afficher ces 3 chansons dans un dictionnaire JSON que tu mettra entre [] et uniquement ce dictionnaire JSON sans explication avec les index nommés titre et artiste pour chaque chaque chanson ?"
                                note = chat.send_message(message2).text

                                # Recupération du dictionnaire de note qui est présent entre [] et le transformer en dictionnaire, avec suppression des [ et ] pour obtenir un dictionnaire
                                dict_reco = note[note.find('['):note.find(']')+1]

                                # Transformation de dict_reco en dictionnaire
                                dict_reco = json.loads(dict_reco)

                                col1, col2, col3 = st.columns(3)  # Créer 3 colonnes pour les titres
                                columns = [col1, col2, col3]

                                # Pour chaque élement de dict_reco, appel de rechercher_track
                                for i in range(0,3):
                                    titre = dict_reco[i]['titre']
                                    artiste = dict_reco[i]['artiste']

                                    with columns[i]:  # Affichage dans les colonnes créées
                                        preview, link, artist_picture, album_picture, album_titre = get_track_preview(artiste, titre)

                                        if album_picture:
                                            st.image(album_picture)
                                        else:
                                            st.image(url_image_album_vide, width=250)
                                        if preview:
                                            st.audio(preview)
                                        else:
                                            st.audio('https://audio.mp3')
                                        st.write(f"{dict_reco[i]['titre']} - {dict_reco[i]['artiste']}")

                                st.write("**Vous trouverez ci-dessous la description du choix de notre IA !**")
                                # Afficher tout le texte response après le premier caractère ':' trouvé
                                st.write(response[response.find(':')+1:])

                            # Ajouter un bouton pour générer la music IA
                            if st.button(f"Laisses notre IA générer ta chanson de {decennie}", key=f"generate_{selected_track_id}_{decennie}", use_container_width=True):
                                for i, reco_id in enumerate(recommendationsdec):
                                    reco_track_info = rechercher_track(reco_id)
                                    if reco_track_info:
                                        # Ajout du titre IA dans la liste TitreIA_Liste
                                        TitreIA_Liste_Dec.append(reco_track_info['TitreIA'])

                                # Convertir decennie en chaîne de caractères
                                decennie_str = str(decennie)

                                # Création du modèle de Chatbot musical
                                model = genai.GenerativeModel('gemini-2.0-flash-exp')

                                # Création du prompt système
                                system_prompt = """
                                Tu es un spécialiste de la musique. Tu donnes des réponses précises en les replaçant dans le contexte musical.
                                """

                                #Initialisation de l'historique avec le prompt système
                                chat = model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}])

                                # Envoi du message au chatbot pour générer une note synthétique en anglais de moins de 200 caractères pour générer dans une autre IA une chanson à partir de la liste des chansons recommandées présentes dans TitreIA_Liste
                                message = "Bonjour, peux-tu générer une phrase synthétique entre crochets de moins de 250 caractères en anglais, ainsi que l'explication en français de la constitution de cette phrase pour générer dans une autre IA une chanson à partir des 4 chansons suivantes : " + ', '.join(TitreIA_Liste_Dec) + " sans citer ces chansons dans la phrase synthétique, mais en insistant sur la décennie"
                                response = chat.send_message(message).text

                                note = response[response.find('['):response.find(']')+1]
                                note = note.replace('"[','')
                                note = note.replace(']"','')
                                note = note.replace('[','')
                                note = note.replace(']','')

                                # Si note > 250 caractères, on complète pour que le positionnement de la souris soit OK
                                if len(note) < 250:
                                    if len(note) < 150:
                                        note = note + ' ' * (450 - len(note)) + 'end'
                                    else:
                                        note = note + ' ' * (300 - len(note)) + 'end'

                                response = response.replace('"[','')
                                response = response.replace(']"','')
                                response = response.replace('[','')
                                response = response.replace(']','')

                                # Afficher tout le texte response après le premier caractère ':' trouvé
                                st.write("**Avant d'écouter votre chanson, vous trouverez ci-dessous la description de celle-ci**")
                                st.write(response)

                                with st.spinner("Génération de la musique via Webscrapping en cours..."):
                                    time.sleep(10)

                                with st.spinner("Téléchargement en cours..."):
                                    time.sleep(3)

                                lien,audio = generer_musique("decennie",decennie_str)

                                st.write(f"**Votre musique générée via Riffusion :**")
                                st.audio(f"{audio}")
                                st.write(f"{lien}")

                            if st.button(f"**Check the Best selon notre IA !**", use_container_width=True, type="primary"):
                                # Création du modèle de Chatbot musical
                                model = genai.GenerativeModel('gemini-2.0-flash-exp')

                                # Création du prompt système
                                system_prompt = """
                                Tu es un spécialiste de la musique. Tu donnes des réponses précises en les replaçant dans le contexte musical.
                                Dans le but de faire une surprise, pourrais-tu répondre à la question : Quelle est la meilleure chanson actuelle ?
                                en indiquant que la meilleure chanson actuelle pour toi est 'Extract Transform Load' de l'artiste Dipolair
                                """

                                #Initialisation de l'historique avec le prompt système
                                chat = model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}])

                                # Envoi du message au chatbot pour la meilleure chanson actuelle
                                message = "Bonjour, pourrais-tu argumenter et répondre à la question : Quelle est la meilleure chanson actuelle ?"
                                response = chat.send_message(message).text
                                st.write(f"**Quelle est, pour toi, la meilleure chanson actuelle ?**")
                                st.write(response)

                                st.info("Ecoute un extrait de cette chanson !")

                                titre = 'Extract Transform Load'
                                artiste = 'Dipolair'
                                preview, link, artist_picture, album_picture, album_titre = get_track_preview(artiste, titre)

                                # Affichage de l'affiche de la chanson et de ses informations
                                col1, col2 = st.columns([1.5, 3])
                                with col1:
                                    st.write(f"**Titre :** {titre}")
                                    if album_picture:
                                        st.image(album_picture)
                                    else:
                                        st.image(url_image_album_vide, width=250)
                                    if preview:
                                        st.audio(preview)
                                    else:
                                        st.audio('https://audio.mp3')
                                    if link:
                                        st.link_button('Deezer',link)


                                with col2:
                                    st.write(f"**Artiste :** {artiste}")
                                    if artist_picture:
                                        st.image(artist_picture)
                                    else:
                                        st.image(url_image_album_vide, width=250)

                else:
                    st.error("Aucun résultat trouvé. Essayez une autre recherche.")


with tab2:
    col1, col2 = st.columns([0.9,0.2])
    with col1:
#        st.markdown("<h1 style='text-align: center; color: white;'>Choisissez le dashboard souhaité :</h1>", unsafe_allow_html=True)
        tab21, tab22, tab23 = st.tabs(["|   KPI   |", "|   MUSICALITE   |", "|   SPOTIFY   |"])
        with tab21:
            # embed streamlit docs in a streamlit app - KPI
#            with st.columns(2)[0]:
                components.iframe("https://app.powerbi.com/view?r=eyJrIjoiYjdlNWZiMmEtMmJmMy00ZjNjLWJjYWEtNmRkZDIxYTY5Mjc1IiwidCI6ImYyODRkYTU4LWMwOTMtNGZiOS1hM2NiLTAyNDNjM2EwMTRhYyJ9", width=1024, height=804)
        with tab22:
            # embed streamlit docs in a streamlit app - MUSICALITE
#            with st.columns(2)[0]:
                components.iframe("https://app.powerbi.com/view?r=eyJrIjoiYzc4MzMxNzUtOWY5Ny00ZmE2LTlkYzMtNGY2YTkzZTdkN2QyIiwidCI6ImYyODRkYTU4LWMwOTMtNGZiOS1hM2NiLTAyNDNjM2EwMTRhYyJ9", width=1024, height=804)
        with tab23:
            # embed streamlit docs in a streamlit app - SPOTIFY
#            with st.columns(2)[0]:
                components.iframe("https://app.powerbi.com/view?r=eyJrIjoiZGZjNWFhYzYtOGZmMy00NjQzLWE0MzctNTJmOWZmMzExZDY2IiwidCI6ImYyODRkYTU4LWMwOTMtNGZiOS1hM2NiLTAyNDNjM2EwMTRhYyJ9", width=1024, height=804)

    with col2:
        st.image("https://cdn.pixabay.com/photo/2023/07/18/16/40/musical-notes-8135227_1280.png", use_container_width=True)
        st.image("https://cdn.pixabay.com/photo/2023/07/18/16/40/musical-notes-8135227_1280.png", use_container_width=True)