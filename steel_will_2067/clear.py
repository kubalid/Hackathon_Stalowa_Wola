import sys
import os

# Dodajemy katalog główny do ścieżek Pythona, żeby skrypt widział folder 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Prawidłowy import obiektu aplikacji Flask oraz bazy danych
from app.app import app
from database import db

def clear_all_data():
    print("Rozpoczynam czyszczenie bazy danych...")
    
    # Usuwa wszystkie tabele
    db.drop_all()
    print("1. Wszystkie tabele i dane zostały usunięte.")
    
    # Tworzy puste tabele na nowo na podstawie modeli
    db.create_all()
    print("2. Utworzono czyste, puste tabele.")
    
    print("\nSukces: Baza danych jest całkowicie czysta i gotowa do pracy!")

if __name__ == '__main__':
    # Uruchomienie w odpowiednim kontekście aplikacji Flask
    with app.app_context():
        clear_all_data()