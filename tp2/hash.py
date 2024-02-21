import PySimpleGUI as sg
import hashlib
import time
import threading

class PasswordCrackerApp:
    def __init__(self):
        self.dictionary_file = ""
        self.password_attempts = 0
        self.start_time = 0
        self.passwords = []
        self.layout = [
            [sg.Text("Dictionnaire:"), sg.InputText(key="-DICTIONARY-"), sg.FileBrowse()],
            [sg.Text("Hash à trouver:"), sg.InputText(key="-HASH-")],
            [sg.Button("Commencer la recherche"), sg.Button("Fermer")],
            [sg.Text("Quantité de mots:"), sg.Text(size=(30, 1), key="-WORD_COUNT-")],
            [sg.Text("Le nombre de tentatives:"), sg.Text(size=(30, 1), key="-ATTEMPTS-")],
            [sg.Text("Le temps cumulé:"), sg.Text(size=(30, 1), key="-TIME-")],
            [sg.Output(size=(50, 10))]
        ]

    sg.theme('DarkAmber')

    def run(self):
        window = sg.Window("Verification MD5", self.layout, finalize=True)

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == "Fermer":
                break
            
            elif event == "Commencer la recherche":
                self.password_attempts = 0
                self.dictionary_file = values["-DICTIONARY-"]
                target_hash = values["-HASH-"]

                if not target_hash or not all(c in "0123456789abcdefABCDEF" for c in target_hash) or len(target_hash) != 32:
                    print("Veuillez entrer un hash MD5 valide.")
                    print("___________________________________________________")
                    continue

                if not self.dictionary_file:
                    print("Veuillez sélectionner un fichier de dictionnaire.")
                    print("___________________________________________________")
                    continue

                self.load_dictionary()
                self.start_time = time.time()

                # Thread pour exécuter la boucle de recherche en arrière-plan
                threading.Thread(target=self.search_password, args=(target_hash, window)).start()

        window.close()

    def search_password(self, target_hash, window):
        for password in self.passwords:
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            if hashed_password == target_hash:
                print(f"Correspondance trouvée ! Mot de passe : {password}")
                sg.PopupNonBlocking(f"Hash : {target_hash }\n  Mot de passe : {password}")
                print("___________________________________________________")
                break

            self.password_attempts += 1
            self.update_attempts_time(window)

        else:
            print("Aucune correspondance trouvée dans le dictionnaire.")
            print("___________________________________________________")

    def load_dictionary(self):
        with open(self.dictionary_file, 'r', encoding='utf-8') as file:
            self.passwords = file.read().splitlines()

    def update_attempts_time(self, window):
        time_elapsed = round(time.time() - self.start_time, 1)

        window["-WORD_COUNT-"].update(value=f" {len(self.passwords)}")
        window["-ATTEMPTS-"].update(value=f" {self.password_attempts}")
        window["-TIME-"].update(value=f" {time_elapsed} secondes")
    
if __name__ == "__main__":
    app = PasswordCrackerApp()
    app.run()
