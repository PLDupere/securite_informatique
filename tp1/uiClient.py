# IMPORTATION
import PySimpleGUI as sg  # https://www.pysimplegui.org/en/latest/  pip install pysimplegui
import socket
import hashlib
from datetime import datetime
import pytz    # https://pypi.org/project/pytz/    pip install pytz
import time                 
import threading

# ATTRIBUTS
CONST_unique_clientId = "12345678" # Need to be fix and can't be change for safaty reason
token = "********"

# Socket Connection
sock_Client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_Client.bind(("127.0.0.2", 6653))  # Fix connection

try:
    sock_Client.connect(("127.0.0.1", 5653))  # Fix connection
except:
    print("CONNECTION FAIL")
    exit()

sg.theme('DarkAmber')

# FONCTIONS
def update_time(window):
    while True:
        token = generate_otp_token()
        window['-TOKEN_TEXT-'].update(f'Token: {token}')
        current_time = 60 - int(datetime.now(pytz.utc).strftime("%S"))
        window['-SECONDS_TEXT-'].update(f'Timer: {current_time}')
        time.sleep(1)

layout = [  [sg.Text('Press send to start app', key='-TOKEN_TEXT-')],
            [sg.Text('Time in seconds', key='-SECONDS_TEXT-'), sg.Text('Wait for confirmation', key='-ACCESS_TEXT-')],
            [sg.Text('Press send to start app', key='-TOKEN_TEXT-')],
            [sg.Text('Enter your token:'), sg.InputText()],
            [sg.Button('Send'), sg.Button('Close')] 
    ]

def generate_otp_token():
    utc_now = datetime.now(pytz.utc)
    minute = int(utc_now.strftime("%M"))
    hour = int(utc_now.strftime("%H"))
    day = int(utc_now.strftime("%d"))
    month = int(utc_now.strftime("%m"))
    year = int(utc_now.strftime("%Y"))

    # Hash
    data_to_hash = f"{minute}{hour}{day}{month}{year}{CONST_unique_clientId}"
    hash_value = hashlib.sha256(data_to_hash.encode()).hexdigest()
    hash_safe = int(hash_value[:8], 16) % (10**8)

    return str(hash_safe)

def send_token(data):
    data = f"{CONST_unique_clientId}|{data}"
    sock_Client.send(str.encode(data, encoding="utf-8"))

layout = [
    [sg.Text('Press send to start app', key='-TOKEN_TEXT-')],
    [sg.Text('Time in seconds', key='-SECONDS_TEXT-'), sg.Text('', key='-ACCESS_TEXT-')],
    [sg.Text('Enter your token'), sg.InputText()],
    [sg.Button('Send'), sg.Button('Close')]
]

window = sg.Window('Token generator', layout, finalize=True)

# Start a separate thread to update the time
update_thread = threading.Thread(target=update_time, args=(window,), daemon=True)
update_thread.start()

# Main loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Close':
        break
    elif event == 'Send':
        send_token(values[0])

    data, address = sock_Client.recvfrom(6653)
    if data:
        data = data.decode(encoding='utf-8')
        window['-ACCESS_TEXT-'].update(f'{data}')
        if(data == "CLOSE"):
            sg.popup_non_blocking("To much try... Lunch the server AGAINT !!")
            time.sleep(2)

        if(data == "Accès confirmé !"):
            sg.popup_non_blocking("Got it. Woo Hoo !!")
        
window.close()