import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail



basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)


app.config['SECRET_KEY'] = '8752e4durtxkseoem73s4ayr'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = MAIL_USERNAME
# app.config['MAIL_PASSWORD'] = MAIL_PASSWORD


db = SQLAlchemy(app)
mail = Mail(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


login_manager.login_view = 'register'
login_manager.login_message_category = 'info'


from library_project import routes
