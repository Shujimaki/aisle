from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Users, db
from .api.phivolcs import get_earthquakes
import regex as re
import json

# contain the routes inside a blueprint
bp = Blueprint("main", __name__)

# sample function for executing a function before the requested route
@bp.before_request
def before_request():
    print("What is love?")

# sample function for executing a function AFTER the requested route
@bp.after_request
def after_request(response):
    print(response)
    return response

# registration route; for checking user details' logic too
@bp.route('/register', methods = ["GET", "POST"])
def register():
    # if method is post, get the form details and check if valid
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        # reject if the username already exists
        if Users.query.filter_by(username=username).first():
            return render_template("register.html", error="Username is already taken")
        
        # reject if the length of the password is less than 12
        if len(password) < 12:
            return render_template("register.html", error="Password must be at least 12 characters")
        
        # reject if the password uses non alphanumeric symbols 
        if not re.match(r"^\w{12,}$", password):
            return render_template("register.html", error="Password characters must be alphanumeric (letters, numbers, or underscore '_')")

        # if all tests above return false, details are valid
        # hence, process the details

        # hash the original password using pbkdf2:sha256
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        
        # create a Users object for the new user
        new_user = Users(username=username, password=hashed_password)

        # add the new user to the database, and commit the changes
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for(".signin"))
    
    # if the request method is GET, simply display the html (the form)
    return render_template("register.html")

# signin route
@bp.route('/signin', methods = ["GET", "POST"])
def signin():
    # if request method is POST, verify if user details are valid for signin
    if request.method == "POST":
        # remove leading and trailing whitespaces
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        # find the username in the database, and return user if found (None if no user is found)
        user = Users.query.filter_by(username=username).first()

        # check if user exists and the unhashed password is the same as the entered password
        if user and check_password_hash(user.password, password):
            # tell the application that the user is logged in
            login_user(user)
            return redirect(url_for(".dashboard"))

        # return to same html with error, if either incorrect username or password
        return render_template("signin.html", error="Invalid username or password")

    # if request method is GET, simply display the html
    return render_template("signin.html")

# signout route
# to be able to sign out, someone must be signed in
@bp.route('/signout')
@login_required
def signout():
    # tell the application that the user is logging out
    logout_user()
    # return to signin route
    return redirect(url_for('.signin'))

# home route
@bp.route('/')
def home():
    return redirect(url_for(".signin"))

# dashboard route
# to access the dashboard, a user must be signed in
@bp.route('/dashboard')
@login_required
def dashboard():
    # get json value from api, and typecast to dict
    earthquake_json = get_earthquakes().get_json()
    return render_template("dashboard.html", username=current_user.username, data=earthquake_json)
    

