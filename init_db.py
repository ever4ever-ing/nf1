from app import app, db, bcrypt
from models import User, Match
from datetime import datetime

with app.app_context():
    # Elimina todas las tablas
    db.drop_all()
   
    # Crea todas las tablas
    db.create_all()

    # Insertar usuarios de ejemplo con contraseñas hasheadas (jugadores de la selección chilena 2011)
    users = [
        User(username='cbravoo', email='cbravoo@example.com', password=bcrypt.generate_password_hash('password1').decode('utf-8'), nombre='Claudio', apellido='Bravo', fecha_nacimiento=datetime(1983, 4, 13)),
        User(username='mriosp', email='mriosp@example.com', password=bcrypt.generate_password_hash('password2').decode('utf-8'), nombre='Mauricio', apellido='Isla', fecha_nacimiento=datetime(1988, 6, 12)),
        User(username='gmedel', email='gmedel@example.com', password=bcrypt.generate_password_hash('password3').decode('utf-8'), nombre='Gary', apellido='Medel', fecha_nacimiento=datetime(1987, 8, 3)),
        User(username='gjaraa', email='gjaraa@example.com', password=bcrypt.generate_password_hash('password4').decode('utf-8'), nombre='Gonzalo', apellido='Jara', fecha_nacimiento=datetime(1985, 8, 29)),
        User(username='mvidal', email='mvidal@example.com', password=bcrypt.generate_password_hash('password5').decode('utf-8'), nombre='Arturo', apellido='Vidal', fecha_nacimiento=datetime(1987, 5, 22)),
        User(username='csanchezz', email='csanchezz@example.com', password=bcrypt.generate_password_hash('password6').decode('utf-8'), nombre='Alexis', apellido='Sánchez', fecha_nacimiento=datetime(1988, 12, 19)),
        User(username='eparedes', email='eparedes@example.com', password=bcrypt.generate_password_hash('password7').decode('utf-8'), nombre='Esteban', apellido='Paredes', fecha_nacimiento=datetime(1980, 8, 1)),
        User(username='jvaldivial', email='jvaldivial@example.com', password=bcrypt.generate_password_hash('password8').decode('utf-8'), nombre='Jorge', apellido='Valdivia', fecha_nacimiento=datetime(1983, 10, 19)),
        User(username='mfernandez', email='mfernandez@example.com', password=bcrypt.generate_password_hash('password9').decode('utf-8'), nombre='Matías', apellido='Fernández', fecha_nacimiento=datetime(1986, 5, 15)),
        User(username='hvargass', email='hvargass@example.com', password=bcrypt.generate_password_hash('password10').decode('utf-8'), nombre='Humberto', apellido='Suazo', fecha_nacimiento=datetime(1981, 5, 10)),
        User(username='jbeausejour', email='jbeausejour@example.com', password=bcrypt.generate_password_hash('password11').decode('utf-8'), nombre='Jean', apellido='Beausejour', fecha_nacimiento=datetime(1984, 6, 1))
    ]

    for user in users:
        db.session.add(user)
    db.session.commit()

    # Insertar partido de ejemplo
    match = Match(title='Partido amistoso Chile 2011', date=datetime(2024, 7, 1, 18, 0), location='Estadio Nacional', organizer_id=1)
    db.session.add(match)
    db.session.commit()

    # Asociar usuarios al partido
    match.players.extend(users)
    db.session.commit()

    print("Datos de prueba insertados con éxito.")