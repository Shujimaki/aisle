from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

# initialize the application's database
db = SQLAlchemy()

# initialize the Users database
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    