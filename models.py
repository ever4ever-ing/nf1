from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Tabla intermedia para la relación muchos-a-muchos
user_match = db.Table('user_match',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('match_id', db.Integer, db.ForeignKey('match.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    apellido = db.Column(db.String(255), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    matches = db.relationship('Match', secondary=user_match, backref=db.backref('players', lazy='dynamic'))
    organized_matches = db.relationship('Match', backref='organizer', lazy='dynamic', foreign_keys='Match.organizer_id')
    friendships = db.relationship('Friendship', foreign_keys='Friendship.user_id', backref='user', lazy='dynamic')
    friend_of = db.relationship('Friendship', foreign_keys='Friendship.friend_id', backref='friend', lazy='dynamic')

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(255), nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_player_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_player_match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    evaluator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    talent_score = db.Column(db.Integer, nullable=False)
    commited_score = db.Column(db.Integer, nullable=False)
    friendliness = db.Column(db.Integer, nullable=False)
    
    player = db.relationship('User', foreign_keys=[match_player_user_id])
    match = db.relationship('Match', foreign_keys=[match_player_match_id])
    evaluator = db.relationship('User', foreign_keys=[evaluator_id])

class MatchComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matchs_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    matchs_organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    match = db.relationship('Match', foreign_keys=[matchs_id])
    organizer = db.relationship('User', foreign_keys=[matchs_organizer_id])
    user = db.relationship('User', foreign_keys=[users_id])