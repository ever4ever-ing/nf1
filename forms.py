from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateTimeField, SelectMultipleField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from models import User
from datetime import datetime

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=255)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    fecha_nacimiento = DateTimeField('Fecha de Nacimiento', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Registrarse')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Ese email ya está en uso. Por favor, elige uno diferente.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class MatchForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    date = DateTimeField('Fecha y Hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Ubicación', validators=[DataRequired()])
    submit = SubmitField('Crear Partido')

    def validate_date(self, date):
        if date.data < datetime.now():
            raise ValidationError('La fecha del partido debe ser en el futuro.')

class EditMatchForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=80)])
    date = DateTimeField('Fecha y Hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    location = StringField('Ubicación', validators=[DataRequired(), Length(max=255)])
    players = SelectMultipleField('Jugadores', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Actualizar Partido')

    def validate_date(self, date):
        if date.data < datetime.now():
            raise ValidationError('La fecha del partido debe ser en el futuro.')

class FeedbackForm(FlaskForm):
    talent_score = IntegerField('Puntuación de Talento', validators=[DataRequired(), NumberRange(min=1, max=5)])
    commited_score = IntegerField('Puntuación de Compromiso', validators=[DataRequired(), NumberRange(min=1, max=5)])
    friendliness = IntegerField('Puntuación de Amigabilidad', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Enviar Feedback')

class MatchCommentForm(FlaskForm):
    comment = TextAreaField('Comentario', validators=[DataRequired(), Length(max=65535)])  # MEDIUMTEXT en MySQL puede almacenar hasta 16MB, pero limitamos a un valor razonable
    submit = SubmitField('Enviar Comentario')
    
class SearchUserForm(FlaskForm):
    search = StringField('Buscar usuario', validators=[DataRequired()])
    submit = SubmitField('Buscar')

    
    
