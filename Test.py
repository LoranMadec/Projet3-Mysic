from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

url = "https://www.riffusion.com"  # Remplace par l'URL réelle

options = Options()
# options.add_argument('--ignore-certificate-errors')  # À utiliser *seulement* en développement, et avec précaution

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    print(driver.title)  # Vérifie si le titre de la page s'affiche
    driver.quit()
except Exception as e:
    print(f"Erreur: {e}")