import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, redirect, url_for, flash
from database import db
from models import Incident

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'instances', 'incidents.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'osiem'
db.init_app(app)

with app.app_context():
    db.create_all()
    print("Baza danych zainicjalizowana poprawnie.")

@app.route('/')
def index():
    return "Aplikacja działa!"

@app.route('/zgloszenie', methods=['GET', 'POST'])
def zgloszenie():
    if request.method == 'POST':
        
        wybrane_zdarzenia = request.form.getlist('zdarzenia')
        opis = request.form.get('opis', '').strip()
        
        if not wybrane_zdarzenia:
            flash("Musisz zaznaczyć przynajmniej jedno zdarzenie!", "error")
            return redirect(url_for('zgloszenie'))
            
        lat_form = request.form.get('lat')
        lng_form = request.form.get('lng')

        if not lat_form or not lng_form:
            flash("Musisz zaznaczyć miejsce zdarzenia na mapie!", "error")
            return redirect(url_for('zgloszenie'))

        incident_type = ", ".join(wybrane_zdarzenia)

        if incident_type == 'Inne':
            wlasna_nazwa = request.form.get('custom_incydent', '').strip()
            if wlasna_nazwa:
                incident_type = wlasna_nazwa

        nowe_zgloszenie = Incident(
            incident_type=incident_type,
            description=opis if opis else None,
            lat=float(lat_form),
            lng=float(lng_form),
            status="Nowe"
        )
        
        db.session.add(nowe_zgloszenie)
        db.session.commit()
        
        flash("Zgłoszenie zostało wysłane pomyślnie!", "success")
        return redirect(url_for('zgloszenie'))
    return render_template('zgloszenie.html')

if __name__ == '__main__':
    app.run(debug=True)