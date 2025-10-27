from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

@app.before_request
def before_request():
    print("What is love?")

@app.after_request
def after_request(response):
    print(response)
    return response

@app.route('/')
def home():
    return render_template('signin.html')

@app.route('/verify_signin', methods=["POST"])
def verify_signin():
    users = {"shuji": "123", "maki": "456"}

    username = request.form.get("username").strip()
    print(username)
    password = request.form.get("password").strip()
    
    print(users.keys())
    if username not in users.keys():
        return "User not found"
    
    if users[username] != password:
        return "Incorrect password"

    return redirect(url_for('dashboard', username=username))



@app.route('/dashboard/<string:username>')
def dashboard(username):
    return f"Welcome to my life, {username}"
    

# add for future login (for chatting with ai)
@app.route('/signin')
def signin():
    return "login here"

if __name__ == "__main__":
    app.run(debug=True)