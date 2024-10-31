import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/nf1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de correo
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER') or 'e4e.1997@gmail.com'
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS') or '12345678asd'
