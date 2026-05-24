import sys
import os
import json
import time
import datetime
import threading
import ollama  
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(CURRENT_DIR) == 'oppanel':
    BASE_DIR = os.path.dirname(CURRENT_DIR)
else:
    BASE_DIR = CURRENT_DIR

sys.path.append(BASE_DIR)
from database import db
from models import Incident, Drone, Department, Drone_category, IncidentAssignment, User

oppanel = Flask(__name__)
oppanel.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'instances', 'incidents.db')}"
oppanel.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
oppanel.config['SECRET_KEY'] = 'panel-operatora-tajny'

db.init_app(oppanel)

from login import auth_bp, login_manager
login_manager.init_app(oppanel)
login_manager.login_view = 'auth.login'
oppanel.register_blueprint(auth_bp)

DRONE_RESPONSE_SCHEMA = {
    'type': 'object',
    'properties': {
        'category_id': {'type': ['integer', 'null']},
        'uzasadnienie': {'type': 'string'}
    },
    'required': ['category_id', 'uzasadnienie']
}

def podpowiedz_drona_przez_ai(incident_type, description):
    kategorie_dronow = Drone_category.query.all()
    lista_dronow = [f"- ID: {k.id}, Model: {k.model}, Opis: {k.description}" for k in kategorie_dronow]
    drony_txt = "\n".join(lista_dronow)

    prompt_systemowy = f"""
    Jesteś elitarnym doradcą zarządzania kryzysowego w Stalowej Woli.
    Przeanalizuj zgłoszenie i dobierz JEDEN, optymalny rodzaj drona do tej sytuacji:
    {drony_txt}
    Zwróć odpowiedź w formacie JSON:
    {{"category_id": int, "uzasadnienie": "Krótkie wyjaśnienie po polsku"}}
    """
    try:
        response = ollama.chat(model='llama3.2', messages=[
            {'role': 'system', 'content': prompt_systemowy},
            {'role': 'user', 'content': f"Typ: {incident_type}. Opis: {description}"}
        ], format=DRONE_RESPONSE_SCHEMA)
        return json.loads(response['message']['content'].strip())
    except:
        return {"category_id": None, "uzasadnienie": "Błąd generowania rekomendacji AI."}


def petla_pracujaca_w_tle(app):
    with app.app_context():
        print("[SYSTEM] Uruchomiono proces rekomendacji AI w tle.")
        while True:
            try:
                nowe_zgloszenia = Incident.query.filter_by(status='Nowe').all()
                for incydent in nowe_zgloszenia:
                    sugestia = podpowiedz_drona_przez_ai(incydent.incident_type, incydent.description)
                    kat_id = sugestia.get('category_id')
                    
                    if kat_id:
                        kat = Drone_category.query.get(kat_id)
                        incydent.status = 'Oczekuje na decyzję'
                        
                        nowe_przypisanie = IncidentAssignment(
                            incident_id=incydent.id,
                            department_id=kat.department_id,
                            allocated_workers=0,  
                            justification=sugestia.get('uzasadnienie')
                        )
                        db.session.add(nowe_przypisanie)
                        db.session.commit()
                        print(f"[AI] Zgłoszenie #{incydent.id} przekazane do weryfikacji dla: {kat.department.name}")
            except Exception as e:
                print(f"[BŁĄD TŁA]: {e}")
            time.sleep(5)


@oppanel.route('/panel')
@login_required
def pokaz_panel():
    if current_user.role != 'Admin':
        username_lower = current_user.username.lower()
        if 'straz' in username_lower:
            return redirect(url_for('panel_sluzby', dept_name='Straz_Pozarna'))
        elif 'policja' in username_lower:
            return redirect(url_for('panel_sluzby', dept_name='Policja'))
        elif 'pogotowie' in username_lower:
            return redirect(url_for('panel_sluzby', dept_name='Pogotowie'))
        elif 'wojsko' in username_lower:
            return redirect(url_for('panel_sluzby', dept_name='Wojsko'))
        
    wszystkie_zgloszenia = Incident.query.order_by(Incident.created_at.desc()).all()
    mapa_sprzetu = {}
    for p in IncidentAssignment.query.all():
        if p.incident:
            zajety_model = "Dron specjalistyczny"
            for kat in p.department.categories:
                if kat.model.lower() in p.justification.lower() or kat.model in p.justification:
                    zajety_model = kat.model
                    break
            if zajety_model == "Dron specjalistyczny" and p.department.categories:
                zajety_model = p.department.categories[0].model
            mapa_sprzetu[p.incident_id] = zajety_model

    return render_template('panel.html', zgloszenia=wszystkie_zgloszenia, mapa_sprzetu=mapa_sprzetu)


@oppanel.route('/sluzba/<string:dept_name>')
@login_required
def panel_sluzby(dept_name):
    nazwy_mapowanie = {'Policja': 'Policja', 'Straz_Pozarna': 'Straż Pożarna', 'Pogotowie': 'Pogotowie Ratunkowe', 'Wojsko': 'Wojsko'}
    
    if current_user.role == 'Operator':
        username_lower = current_user.username.lower()
        wybrany_parametr = dept_name.lower().replace('_pozarna', '')
        
        if wybrany_parametr not in username_lower:
            return f"Brak uprawnień dostępu do panelu {dept_name} dla konta {current_user.username}! (403 Forbidden)", 403

    db_name = nazwy_mapowanie.get(dept_name)
    department = Department.query.filter_by(name=db_name).first_or_404()
    
    db.session.expire_all()
    uzytkownik_db = User.query.get(current_user.id)
    
    drony_sluzby = []
    for kategoria in department.categories:
        for dron in kategoria.instances:
            zadanie = "Gotowość w hangarze"
            inc_id = None
            
            aktywne_p = IncidentAssignment.query.filter_by(allocated_workers=dron.id).join(Incident).filter(Incident.status == 'W akcji').first()
            
            if dron.status == 'Niedostępny' and aktywne_p and aktywne_p.incident:
                zadanie = f"W locie: Zgłoszenie #{aktywne_p.incident.id}"
                inc_id = aktywne_p.incident.id
                    
            drony_sluzby.append({
                'id': dron.id,
                'model': kategoria.model,
                'status': dron.status,
                'zadanie': zadanie,
                'incident_id': inc_id,
                'uprawniony': kategoria in uzytkownik_db.permitted_categories
            })

    akcje = Incident.query.join(IncidentAssignment).filter(
        IncidentAssignment.department_id == department.id,
        Incident.status == 'Oczekuje na decyzję'
    ).all()

    return render_template(
        'sluzba.html', 
        department=department, 
        drony=sorted(drony_sluzby, key=lambda x: x['id']), 
        akcje=akcje,
        dept_url=dept_name
    )


@oppanel.route('/sluzba/decyzja/<string:action>/<string:dept_name>/<int:incident_id>')
@login_required
def decyzja_operatora(action, dept_name, incident_id):
    incydent = Incident.query.get_or_404(incident_id)
    przypisanie = IncidentAssignment.query.filter_by(incident_id=incydent.id).first_or_404()
    uzytkownik_db = User.query.get(current_user.id)

    if action == 'odrzuc':
        incydent.status = 'Nowe'
        db.session.delete(przypisanie)
        db.session.commit()
        return redirect(url_for('panel_sluzby', dept_name=dept_name))

    if action == 'troll':
        incydent.status = 'Anulowane (Troll)'
        db.session.commit()
        return redirect(url_for('panel_sluzby', dept_name=dept_name))

    if action == 'przyjmij':
        juz_steruje = IncidentAssignment.query.filter_by(user_id=uzytkownik_db.id).join(Incident).filter(Incident.status == 'W akcji').first()
        if juz_steruje:
            flash("Błąd: Jako operator sterujesz już aktywną misją w terenie! Sprowadź najpierw poprzedniego drona.", "error")
            return redirect(url_for('panel_sluzby', dept_name=dept_name))

        wybrana_kat = None
        for kat in przypisanie.department.categories:
            if kat.model.lower() in przypisanie.justification.lower() or kat.model in przypisanie.justification:
                wybrana_kat = kat
                break
        if not wybrana_kat and przypisanie.department.categories:
            wybrana_kat = przypisanie.department.categories[0]

        if wybrana_kat not in uzytkownik_db.permitted_categories:
            flash(f"Błąd: Nie posiadasz uprawnień licencji i certyfikacji na model: {wybrana_kat.model}!", "error")
            return redirect(url_for('panel_sluzby', dept_name=dept_name))

        wolny_dron = Drone.query.filter_by(category_id=wybrana_kat.id, status='Dostępny').first()
        if not wolny_dron:
            flash(f"Błąd: Wszystkie drony typu {wybrana_kat.model} są aktualnie w powietrzu lub serwisie!", "error")
            return redirect(url_for('panel_sluzby', dept_name=dept_name))

        wolny_dron.status = 'Niedostępny'
        incydent.status = 'W akcji'
        
        przypisanie.user_id = uzytkownik_db.id
        przypisanie.allocated_workers = wolny_dron.id 
        przypisanie.assigned_at = datetime.datetime.now()
        
        db.session.commit()
        return redirect(url_for('panel_sluzby', dept_name=dept_name))

    return "Nieznana akcja", 400


@oppanel.route('/sluzba/zakoncz-misje/<string:dept_name>/<int:drone_id>/<int:incident_id>')
@login_required
def zakoncz_misje_sluzby(dept_name, drone_id, incident_id):
    dron = Drone.query.get_or_404(drone_id)
    incydent = Incident.query.get_or_404(incident_id)
    przypisanie = IncidentAssignment.query.filter_by(incident_id=incydent.id).first()

    dron.status = 'Regeneracja'
    incydent.status = 'Zamknięte'
    if przypisanie:
        przypisanie.finished_at = datetime.datetime.now()
    db.session.commit()

    def serwis_techniczny(d_id):
        time.sleep(20)
        with oppanel.app_context():
            d = Drone.query.get(d_id)
            if d:
                d.status = 'Dostępny'
                db.session.commit()
                print(f"[SERWIS] Dron #D-{d_id} pomyślnie zregenerowany.")
                
    threading.Thread(target=serwis_techniczny, args=(dron.id,), daemon=True).start()
    return redirect(url_for('panel_sluzby', dept_name=dept_name))


@oppanel.route('/zamknij/<int:incident_id>')
@login_required
def zamknij_zgloszenie(incident_id):
    incydent = Incident.query.get_or_404(incident_id)
    incydent.status = 'Zamknięte'
    db.session.commit()
    return redirect(url_for('pokaz_panel'))


@oppanel.route('/sluzba/aktywuj-drona/<string:dept_name>/<int:drone_id>')
@login_required
def aktywuj_drona(dept_name, drone_id):
    dron = Drone.query.get_or_404(drone_id)
    if dron.status == 'Regeneracja':
        dron.status = 'Dostępny'
        db.session.commit()
    return redirect(url_for('panel_sluzby', dept_name=dept_name))


if __name__ == '__main__':
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        threading.Thread(target=petla_pracujaca_w_tle, args=(oppanel,), daemon=True).start()
    oppanel.run(debug=True, port=5001)