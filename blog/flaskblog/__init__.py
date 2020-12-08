import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


app = Flask(__name__)
app.config['SECRET_KEY'] = '664215d7c64db6722344a4b097da692d' #import secrets---secrets.token_hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)


'''
By default, when a user attempts to access a login_required view without being logged in,
Flask-Login will flash a message and redirect them to the log in view. 
(If the login view is not set, it will abort with a 401 error.)
'''
login_manager.login_view = 'login' # login is the function name.
login_manager.login_message_category= "warning"
#login_manager.login_message = u"Please Login to access this page"

from flaskblog import routes
'''This import is here because when we import any module python runs that whole script(routes.py) here.
And that will give error because in on importing routes.py it'll will run whole module and in 3rd like app is imported, so we need 
create an app first.
'''
