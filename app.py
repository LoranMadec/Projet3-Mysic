import streamlit as st
import pandas as pd
import gdown
import json
import streamlit.components.v1 as components
from streamlit.components.v1 import html

import time
import numpy as np
import requests

from helium import *
import mouse
import pyperclip


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

import google.generativeai as genai

GOOGLE_API_KEY='AIzaSyBQLR4y1s7SycCHfBLbJSggFJaRGMo2Zgo'
genai.configure(api_key=GOOGLE_API_KEY)

# Clé pour Riffusion
user = 'laurent.lolo.madec@gmail.com'
pwd='H3c+Y8t*75<^)CD'

###
### Définition des fonctions
###
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

# Fonction pour charger les données à partir d'un fichier JSON => pas utilisé car moins performante qu'avec le CSV
def load_data2():
    # Charger fichier JSON dans un DataFrame
    df_original = pd.read_json("df_streamlit.json")
    suggestions = df_original['Combined'].tolist()
    df = df_original[["id", "titre", "popularity", "artists", "release_date", "decennie", "durée", "genres", "TitreIA"]]
    return df, suggestions


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
        st.error("Erreur JSON : ",e)
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
        # Afficher l'erreur dans Streamlit
        st.error(f"Erreur reco_genre : {e}")
        return []
    

# Fonction pour obtenir les recommandations d'un track en fonction de sa décennie
def get_recommendations_par_decennie(decennie, id_track):
    recommendations = []
    try:
        decennie_str = str(decennie)
        if decennie_str in chemins_json:
            decennie_json = charger_json(chemins_json[decennie_str])
            for item in decennie_json:
                if item['id_track'] == id_track:
                    for i in range(1, 4):  # Pour les 3 recommandations possibles
                        reco_id = item.get(f'id_reco{i}')
                        if reco_id:
                            recommendations.append(reco_id)
        return recommendations

    except Exception as e:
        # Afficher l'erreur dans Streamlit
        st.error(f"Erreur reco_decennie : {e}")
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


# Fonction pour générer une musique à partir d'un prompt

def generer_musique(prompt):

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Indispensable pour Streamlit
    chrome_options.add_argument("--no-sandbox")  # *Essentiel* pour Streamlit
    chrome_options.add_argument("--disable-dev-shm-usage")  # Important pour Streamlit
    chrome_options.add_argument("--remote-debugging-port=9222") # Ajoute ce port

    # Chemin vers Chromium (CRUCIAL)
    chromium_binary = "/usr/bin/chromium" # ou /usr/bin/chromium
    chrome_options.binary_location = chromium_binary

    service = Service(executable_path=chromium_binary) # Use Service object

    browser = webdriver.Chrome(service=service, options=chrome_options)


#    chrome_options = Options()
#    chrome_options.add_argument("--headless")  # Mode headless
#    chrome_options.add_argument("--no-sandbox")  
#    chrome_options.add_argument("--disable-dev-shm-usage")  
#    chrome_options.add_argument("--remote-debugging-port=9222") 
#    chrome_options.add_argument("--no-sandbox")  # Mode headless
#    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Désactiver la détection automatisée
#    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
#   user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
#    options = {"arguments": ["user-agent={user_agent}"]}
#    browser = start_chrome( options=chrome_options, headless=True)

    # Ouvrir le navigateur et aller sur le site riffusion
#    browser = start_chrome()
    go_to('https://www.riffusion.com')
    # Cliquez sur le bouton Login
    click('Login')
    # Cliquez sur le bouton Continue with Discord
    click('Continue with Discord')
    time.sleep(2)

    # Remplir le formulaire avec E-mail = user et Password = pwd
    write(user, into='E-MAIL OU NUMÉRO DE TÉLÉPHONE*')
    write(pwd, into='MOT DE PASSE*')
    # Cliquez sur le bouton Connexion
    click('Connexion')
    # Cliquez sur le texte 
    click('Accéder à ton adresse')
    # Déplacement de 2 tabulations et de 2 fleches vers le bas
    actions = ActionChains(browser)
    actions.send_keys(Keys.TAB).perform()
    actions.send_keys(Keys.TAB).perform()

    actions.send_keys(Keys.ARROW_DOWN).perform()
    actions.send_keys(Keys.ARROW_DOWN).perform()

    # Attendre 0.5 secondes
    time.sleep(0.2)
    # Cliquez sur le bouton Connexion
    click('Autoriser')
    # Attendre 1 secondes
    time.sleep(0.2)    
    
    # Click Sur Create the music you imagine...
    click('Create the music you imagine...')

    # Ecrire le texte dans le champ Create the music you imagine...
    write(prompt, into='Create the music you imagine...')
    time.sleep(0.1)    
    # Positionner la souris au milieu de l'écran
    # Click Sur Entrée
    actions.send_keys(Keys.ENTER).perform()

    time.sleep(55)

    # Cliquez sur le 1er bouton More options
    click('More options')
    # Cliquez sur le bouton Copy link
    click('Copy link')
    # Récupérer le lien copié dans le presse-papier
    lien = pyperclip.paste()
    # Fermer le navigateur
#    browser.quit()

    return lien


#########################################################################################
#########################################################################################
#########################################################################################
# --- PAGE CONFIGURATION ---

st.set_page_config(page_title = "Application de recommandations de musique", page_icon = ":notes_de_musique:", layout = "wide")

# Removing whitespace from the top of the page
st.markdown("""
<style>
.css-18e3th9 { padding-top: 0rem; padding-bottom: 10rem; padding-left: 5rem; padding-right: 5rem; }
.css-1d391kg { padding-top: 3.5rem; padding-right: 1rem; padding-bottom: 3.5rem; padding-left: 1rem; }
</style>""", unsafe_allow_html=True)
st.logo("https://thumbs.dreamstime.com/z/music-logo-icon-vector-design-illustration-template-symbol-sound-element-musical-audio-modern-graphic-creative-abstract-company-170538718.jpg", size="large", link=None, icon_image=None)

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
                                st.write(f"**Artiste :** {track_info['Artiste']}")
                                st.write(f"**Date de Sortie :** {track_info['DateSortie']}")
                                st.write(f"**Genres :** {track_info['Genre']}")
                                st.write(f"**Durée :** {track_info['Durée']}")
                                st.write(f"**Note de popularité :** {track_info['NotePopularité']}")

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
                                message = "Bonjour, peux-tu générer une phrase synthétique entre crochets de moins de 250 caractères en anglais, ainsi que l'explication en français de la constitution de cette phrase pour générer dans une autre IA une chanson à partir des 4 chansons suivantes : " + ', '.join(TitreIA_Liste_Genre)   
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

                                lien = generer_musique(note)
                                st.write(f"**Voici le lien de votre musique générée via Riffusion :**")
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

                                # Création du modèle de Chatbot musical
                                model = genai.GenerativeModel('gemini-2.0-flash-exp')

                                # Création du prompt système
                                system_prompt = """
                                Tu es un spécialiste de la musique. Tu donnes des réponses précises en les replaçant dans le contexte musical.
                                """

                                #Initialisation de l'historique avec le prompt système
                                chat = model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}])

                                # Envoi du message au chatbot pour générer une note synthétique en anglais de moins de 200 caractères pour générer dans une autre IA une chanson à partir de la liste des chansons recommandées présentes dans TitreIA_Liste
                                message = "Bonjour, peux-tu générer une phrase synthétique entre crochets de moins de 250 caractères en anglais, ainsi que l'explication en français de la constitution de cette phrase pour générer dans une autre IA une chanson à partir des 4 chansons suivantes : " + ', '.join(TitreIA_Liste_Dec)   
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

                                lien = generer_musique(note)
                                st.write(f"**Voici le lien de votre musique générée via Riffusion :**")
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
    st.header("KPIs sur MyZic") 