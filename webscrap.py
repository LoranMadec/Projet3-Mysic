from helium import *
import time
import mouse
import pyperclip

user = 'laurent.lolo.madec@gmail.com'
pwd='H3c+Y8t*75<^)CD'

def generer_musique(prompt):

    # Ouvrir le navigateur et aller sur le site riffusion
    browser = start_chrome()
    go_to('https://www.riffusion.com')
    # Cliquez sur le bouton Login
    click('Login')
    # Cliquez sur le bouton Continue with Discord
    click('Continue with Discord')
    time.sleep(1)


    # Remplir le formulaire avec E-mail = user et Password = pwd
    write(user, into='E-MAIL OU NUMÉRO DE TÉLÉPHONE*')
    write(pwd, into='MOT DE PASSE*')
    # Cliquez sur le bouton Connexion
    click('Connexion')
    # Cliquez sur le texte 
    click('Accéder à ton adresse')
    # Positionner la souris au milieu de l'écran
    mouse.move(500, 500)
    # Scroll down
    mouse.wheel(-1)
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
    # Positionner la souris au milieu de l'écran
    mouse.move(900, 350)
    mouse.click(button='left')

    time.sleep(55)

    # Cliquez sur le 1er bouton More options
    click('More options')
    # Cliquez sur le bouton Copy link
    click('Copy link')
    # Récupérer le lien copié dans le presse-papier
    lien = pyperclip.paste()
    # Fermer le navigateur
    kill_browser()

    return lien

note="Compose a jazz piece blending Sinatra's romantic sentimentality, Ellington and Coltrane's sophisticated harmonic interplay and improvisational freedom, and Brubeck's innovative rhythmic structures, incorporating a hint of classical elegance"

print(len(note))

lien = generer_musique(note)

print(lien)