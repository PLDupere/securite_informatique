#IMPORTATION
import os
import socket
import hashlib
from datetime import datetime
import pytz     # https://pypi.org/project/pytz/    pip install pytz
import threading
import time
import sys

#CONNECTION
sock_Server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_Server.bind(("127.0.0.1", 5653))   # Fix connection server

#ATTRIBUTS
client_id = "12345678"  # Not fix. Will change with clienId
client_token = ""
server_answer = ""
client_address= ""
client_port = ""
client_try = 0
last_token = "********"
actual_token = "********"
buffer_token = "********"

token_lock = threading.Lock()

#FONCTIONS
def get_client_id(data):
    unique_id = data.split("|")[0]
    return unique_id

def get_client_token(data):
    client_token = data.split("|")[1]
    return client_token

def generate_otp_token():
    utc_now = datetime.now(pytz.utc)
    minute = int(utc_now.strftime("%M"))
    hour = int(utc_now.strftime("%H"))
    day = int(utc_now.strftime("%d"))
    month = int(utc_now.strftime("%m"))
    year = int(utc_now.strftime("%Y"))

    # Hash
    data_to_hash = f"{minute}{hour}{day}{month}{year}{client_id}"
    hash_value = hashlib.sha256(data_to_hash.encode()).hexdigest()
    hash_safe = int(hash_value[:8], 16) % (10**8)

    return str(hash_safe)

def verify_otp_token(client_id, client_token, nb_try):
    actual_token = generate_otp_token()

    if (nb_try >= 4):
        return "CLOSE"
    if actual_token == str(client_token):
        return "Accès confirmé !"
    else:
        return "Accès refusé !"
    
def send_answer(client_id, client_address, client_port, data):
    try:
        sock_Server.connect((client_address, client_port)) # Fix connection server
    except:
        print("CONNECTION FAIL")
        exit()
    
    if data:
        data = f"{data}" 
        sock_Server.send(str.encode(data, encoding="utf-8"))

def add_try():
    global client_try
    client_try += 1

def get_try():
    return client_try

def print_last_token():
    global buffer_token
    global last_token

    while True:
        actual_token = generate_otp_token()
        
        with token_lock:
            if actual_token != buffer_token:
                last_token = buffer_token
                buffer_token = actual_token

            # Show last token on the console
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"The last token was {last_token}.")
            #print(f"The actual is {actual_token}.")

        time.sleep(1)

        
# Start a separate thread to update the LAST TOKEN
threading.Thread(target=print_last_token, daemon=True).start()

# Main loop
while True:
    data, address = sock_Server.recvfrom(4096)
    actual_token = generate_otp_token()
    
    if data: 
        data = data.decode(encoding='utf-8')

        # Get informations from client
        client_id = get_client_id(data)
        client_token = get_client_token(data)
        client_address = address[0]
        client_port = address[1]

        server_answer = verify_otp_token(client_id, client_token, client_try)

        # See server operation
        # print(f"{server_answer} | You have make {client_try + 1} try.")

        # Dynamic connection client
        send_answer(client_id, client_address, client_port,server_answer) 
        
        # Close server and connection
        add_try()
        client_try = get_try()
        if (client_try > 4):
            sock_Server.close()
            sys.exit()