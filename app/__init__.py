
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager

from .models import db, Users
from .routes import bp as main_bp

# initialize the login manager that will handle the authentication and authorization
login_manager = LoginManager()

# initialize the function for the login manager to call for every logged in user's action
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# initialize the app variable
def create_app():

    # make app a Flask object and get the configurations
    app = Flask(__name__)
    app.config.from_object("config.DevelopmentConfig")

    # initialize the database to connect to the app object
    db.init_app(app)
    login_manager.init_app(app)
    # set the login view of the login manager (the signin route)
    login_manager.login_view = ".signin"
    
    # create the database (initialized via models.py)
    with app.app_context():
        db.create_all()
    
    # register the main blueprint from routes.py to the application
    app.register_blueprint(main_bp)

    return app

