from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from config import Config
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from routes import *  # Añade esta línea aquí

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)