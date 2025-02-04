from helium import *
import time
import mouse
import pyperclip

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


user = 'laurent.lolo.madec@gmail.com'
pwd='H3c+Y8t*75<^)CD'

def generer_musique(prompt):

#    options.add_argument("--no-sandbox")  
#    options.add_argument("--disable-dev-shm-usage")  
#    options.add_argument("--remote-debugging-port=9222") 

#   driver = webdriver.Chrome(options=options)

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Mode headless
    chrome_options.add_argument("--no-sandbox")  
    chrome_options.add_argument("--disable-dev-shm-usage")  
    chrome_options.add_argument("--remote-debugging-port=9222") 
#    chrome_options.add_argument("--no-sandbox")  # Mode headless
#    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Désactiver la détection automatisée
#    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    options = {"arguments": ["user-agent={user_agent}"]}
    browser = start_chrome( options=chrome_options, headless=True)

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

note="Compose a jazz piece blending Sinatra's romantic sentimentality, Ellington and Coltrane's sophisticated harmonic interplay and improvisational freedom, and Brubeck's innovative rhythmic structures, incorporating a hint of classical elegance"


lien = generer_musique(note)

print(lien)