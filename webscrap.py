from helium import *
import time
import mouse
import pyperclip

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By  # Importez By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


user = 'laurent.lolo.madec@gmail.com'
pwd='H3c+Y8t*75<^)CD'

def driver_init():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    return driver

def generer_musique(prompt):

    driver = driver_init()
    driver.get("https://www.riffusion.com")

    try:
    # Attendre au maximum 10 secondes que le bouton Login soit cliquable
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Generate')]")))
        login_button.click()

        discord_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue with Discord')]")))
        discord_button.click()

        time.sleep(2)

        email_field = driver.find_element_by_xpath('//*[@id="email"]')))
#        password_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="Mot de passe"]')))
#        password_field = driver.find_element_by_xpath('//*[@id="Mot de passe"]')
        
        lien = "OK"

    except TimeoutException:
        print("Le bouton  n'a pas été trouvé après 10 secondes.")
        lien ="Le bouton  n'a pas été trouvé après 10 secondes."
    except Exception as e: # Pour les autres erreurs (par exemple, si le texte change)
        print(f"Une autre erreur est survenue : {e}")
        lien = f"Une autre erreur est survenue : {e}"

    return lien

note="Compose a jazz piece blending Sinatra's romantic sentimentality, Ellington and Coltrane's sophisticated harmonic interplay and improvisational freedom, and Brubeck's innovative rhythmic structures, incorporating a hint of classical elegance"


lien = generer_musique(note)

print(lien)