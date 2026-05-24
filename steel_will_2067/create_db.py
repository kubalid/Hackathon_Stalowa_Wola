import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app
from database import db
# Importujemy nowe modele User i tabelę pośrednią uprawnień
from models import Department, Incident, Drone, Drone_category, User
from werkzeug.security import generate_password_hash

def run_tests():
    print("--- ROZPOCZĘCIE TESTU KATEGORII, INSTANCJI DRONÓW ORAZ OPERATORÓW ---")
    

    db.drop_all()
    db.create_all()
    print("1. Wyczyszczono i utworzono tabele na nowo.")


    straz = Department(name="Straż Pożarna")
    policja = Department(name="Policja")
    pogotowie = Department(name="Pogotowie Ratunkowe")
    wojsko = Department(name="Wojsko")
    
    db.session.add_all([straz, policja, pogotowie, wojsko])
    db.session.commit()
    print("2. Dodano działy: Strażacy, Policjanci, Pogotowie, Wojsko.")

   
    kat_p_patrol = Drone_category(model="Dron patrolowy", description="Małe drony, kamera, zasieg do 10 km np. DJI Mini 4 Pro", department=policja)
    kat_p_taktyk = Drone_category(model="Dron taktyczny", description="termowizja, laserowy dalmierz, głośnik, reflektor np. Autel EVO Max 4T", department=policja)
    
    
    kat_s_gasisz = Drone_category(model="Dron taktyczno-gaśniczy", description="Kamera termowizyjna, dalmierz do wykrywania źródeł ognia", department=straz)
    kat_s_ciezki = Drone_category(model="Dron gaśniczy", description="udźwig do ok. 30 kg do gaszenia małych pożarów punktowo", department=straz)

    kat_r_rozpoznanie = Drone_category(model="Dron rozpoznawczy", description="Kamera, głośnik do komunikacji, możliwość zrzutu małego pakietu", department=pogotowie)
    kat_r_transport = Drone_category(model="Dron transportowy", description="transport leków, krwi, sprzętu w niedostępne miejsca", department=pogotowie)
    
  
    kat_w_mikro = Drone_category(model="Dron mikrotaktyczny", description="Mikrodron z kamerą zasięg do 2 km, obserwacja bliskiego otoczenia", department=wojsko)
    kat_w_operacyjny = Drone_category(model="Dron operacyjny", description="monitorowanie pola walki, korekta ognia, duży rozmiar i zasięg", department=wojsko)

    db.session.add_all([
        kat_p_patrol, kat_p_taktyk, 
        kat_s_gasisz, kat_s_ciezki, 
        kat_r_rozpoznanie, kat_r_transport, 
        kat_w_mikro, kat_w_operacyjny
    ])
    db.session.commit()
    print("3. Utworzono szablony kategorii produktowych dronów.")


    haslo_testowe = generate_password_hash("haslo123")
    

    konto_admina = User(username="admin", password_hash=haslo_testowe, role="Admin", active=True)
    
    op_policja = User(username="operator_policja", password_hash=haslo_testowe, role="Operator", active=True)
    op_straz = User(username="operator_straz", password_hash=haslo_testowe, role="Operator", active=True)
    op_pogotowie = User(username="operator_pogotowie", password_hash=haslo_testowe, role="Operator", active=True)
    op_wojsko = User(username="operator_wojsko", password_hash=haslo_testowe, role="Operator", active=True)
    
   
    op_policja_patrol = User(username="operator_policja_patrol", password_hash=haslo_testowe, role="Operator", active=True)
    
  
    op_policja.permitted_categories.extend([kat_p_patrol])
    op_straz.permitted_categories.extend([kat_s_gasisz, kat_s_ciezki])
    op_pogotowie.permitted_categories.extend([kat_r_rozpoznanie, kat_r_transport])
    op_wojsko.permitted_categories.extend([kat_w_mikro, kat_w_operacyjny])
   
    op_policja_patrol.permitted_categories.extend([kat_p_taktyk])
    
    # Dodajemy wszystkich użytkowników do bazy
    db.session.add_all([konto_admina, op_policja, op_straz, op_pogotowie, op_wojsko, op_policja_patrol])
    db.session.commit()
    print("4. Utworzono konta operatorów, konto admina oraz dedykowanego operatora z jedną licencją.")


    fizyczne_drony = []

    for _ in range(3):
        fizyczne_drony.append(Drone(category=kat_p_patrol, status="Dostępny"))
        fizyczne_drony.append(Drone(category=kat_p_taktyk, status="Dostępny"))
        fizyczne_drony.append(Drone(category=kat_s_gasisz, status="Dostępny"))
        fizyczne_drony.append(Drone(category=kat_s_ciezki, status="Dostępny"))

    for _ in range(2):
        fizyczne_drony.append(Drone(category=kat_r_rozpoznanie, status="Dostępny"))
        fizyczne_drony.append(Drone(category=kat_r_transport, status="Dostępny"))
        fizyczne_drony.append(Drone(category=kat_w_mikro, status="Dostępny"))
        fizyczne_drony.append(Drone(category=kat_w_operacyjny, status="Dostępny"))

    db.session.add_all(fizyczne_drony)
    db.session.commit()
    print(f"5. Pomyślnie wygenerowano i zarejestrowano {len(fizyczne_drony)} fizycznych urządzeń w bazach jednostek.")


    print("\n--- AKTUALNY STAN FLOTY DRONÓW (Z PODZIAŁEM NA SŁUŻBY) ---")
    print(f"Liczba zgłoszeń w bazie: {Incident.query.count()}")
    print(f"Liczba operatorów w bazie: {User.query.count()}")
    print(f"Wszystkie drony Policji:   {policja.total_resources} szt. (Wolne: {policja.available_resources})")
    print(f"Wszystkie drony Straży:    {straz.total_resources} szt. (Wolne: {straz.available_resources})")
    print(f"Wszystkie drony Pogotowia: {pogotowie.total_resources} szt. (Wolne: {pogotowie.available_resources})")
    print(f"Wszystkie drony Wojska:    {wojsko.total_resources} szt. (Wolne: {wojsko.available_resources})")

    print("\nTEST ZALICZONY: Struktura wielopoziomowa wraz z kontami użytkowników została poprawnie zasilona.")

if __name__ == '__main__':
    with app.app_context():
        run_tests()