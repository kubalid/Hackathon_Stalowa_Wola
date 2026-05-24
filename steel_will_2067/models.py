from datetime import datetime
from database import db

# Tabela łącząca (wiele-do-wielu) określająca, którzy operatorzy mogą sterować jakimi kategoriami dronów
user_drone_permissions = db.Table('user_drone_permissions',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('drone_categories.id', ondelete='CASCADE'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='Operator', nullable=False)  # Administrator / Operator
    active = db.Column(db.Boolean, default=True, nullable=False)          # Status aktywności operatora
    
    # RELACJE
    # Uprawnienia operatora do sterowania określonym typem sprzętu
    permitted_categories = db.relationship('Drone_category', secondary=user_drone_permissions, backref=db.backref('permitted_operators', lazy='dynamic'))
    assignments = db.relationship('IncidentAssignment', backref='operator', lazy=True)


class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    
    categories = db.relationship('Drone_category', backref='department', lazy=True)
    assignments = db.relationship('IncidentAssignment', backref='department', lazy=True)

    @property
    def total_resources(self):
        total = 0
        for category in self.categories:
            total += len(category.instances)
        return total

    @property
    def busy_resources(self):
        total_busy = 0
        for assignment in self.assignments:
            if assignment.incident and assignment.incident.status in ['W akcji', 'Przeanalizowano']:
                total_busy += assignment.allocated_workers
        return total_busy

    @property
    def available_resources(self):
        return self.total_resources - self.busy_resources


class Drone_category(db.Model):
    __tablename__ = 'drone_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(50), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)

    instances = db.relationship('Drone', backref='category', lazy=True)


class Drone(db.Model):
    __tablename__ = 'drones'
    
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='Dostępny', nullable=False) # Dostępny / Niedostępny / Regeneracja       
    category_id = db.Column(db.Integer, db.ForeignKey('drone_categories.id'), nullable=True)


class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_type = db.Column(db.String(255), nullable=False) 
    description = db.Column(db.Text, nullable=True)
    phonenumber = db.Column(db.String(20), nullable=True)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False) # Kiedy przyszło zgłoszenie
    status = db.Column(db.String(40), default='Nowe', nullable=False)          # Nowe / Oczekuje na operatora / W akcji / Zamknięte / Anulowane (Troll)
    
    assignments = db.relationship('IncidentAssignment', backref='incident', lazy=True)


class IncidentAssignment(db.Model):
    __tablename__ = 'incident_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Jaki operator pilotuje misję
    
    allocated_workers = db.Column(db.Integer, nullable=False, default=0) # 0 - rekomendacja, 1 - lot zatwierdzony
    
    # Logi i czasy operacyjne
    justification = db.Column(db.Text, nullable=True)                    # Sugestia od AI (Rekomendacja)
    assigned_at = db.Column(db.DateTime, nullable=True)                  # Kiedy operator wystartował (Rozpoczęcie)
    finished_at = db.Column(db.DateTime, nullable=True)                  # Kiedy ukończono misję (Zakończenie)
    operator_notes = db.Column(db.Text, nullable=True)                   # Opis przebiegu akcji spisany przez człowieka