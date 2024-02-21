import PySimpleGUI as sg    # pip install PySimpleGUI
import itertools            # pip install more-itertools
import os

sg.theme('DarkAmber')

def generate_password_dictionary(min_length, max_length, allowed_characters, output_file):
    if not output_file.endswith('.txt'):
        output_file += '.txt'

    with open(output_file, 'w') as file:
        for length in range(min_length, max_length + 1):
            for password in itertools.product(allowed_characters, repeat=length):
                file.write(''.join(password) + '\n')

def main():
    layout = [
        [sg.Text('Longueur minimale des mots de passe du dictionnaire'), sg.InputText()],
        [sg.Text('Longueur maximale des mots de passe du dictionnaire'), sg.InputText()],
        [sg.Text('Caractères permis dans le dictionnaire'), sg.InputText()],
        [sg.Text('Le dossier et le nom de fichier de sortie'), sg.InputText(default_text=os.path.expanduser('~\\motdepasse.txt'))], # impossible d'écrire sur le c: directement
        [sg.Button('Générer'), sg.Button('Fermer')]
    ]

    window = sg.Window('Générateur de mot de passes', layout, finalize=True)
    sg.theme('DarkAmber')

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Fermer':
            break

        elif event == 'Générer':
            try:
                min_length = int(values[0])
                max_length = int(values[1])
                allowed_characters = values[2]
                output_file = values[3]

                generate_password_dictionary(min_length, max_length, allowed_characters, output_file)

                sg.popup('Dictionnaire généré avec succès!')
            except ValueError:
                sg.popup_error('Veuillez saisir des valeurs valides pour la longueur des mots de passe.')

    window.close()

if __name__ == "__main__":
    main()
