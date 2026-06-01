import json  
import hashlib # biblioteka która zawiera algprytymy do hashowania haseł 
import streamlit as st
from pathlib import Path

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest() #enocode  zamienia tekst na bajty bo SHA-256 potrzebuje bajtów, nie tekstu
# scrambles the bytes 
# hexidigest zamienia wynik na czytelny ciąg znaków np. "b94d27..."
def load_users(): # ładuje użytkowników z pliku users.json
    if Path("users.json").exists():
        with open("users.json", "r") as f: #read otwiera plik do czytania 
            return json.load(f)
    return {}

def save_users(users):# zapisuje użytkowników do pliku users.json
    with open("users.json", "w") as f:#write otwiera plik do zapisywania. 
        json.dump(users, f)

# bez tych funkcji aplikacja dzialala by do momentu zamkniecia okna po tym resetowal by sie i nie dalo by sie zalogowac 
