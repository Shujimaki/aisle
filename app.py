from flask import Flask, redirect, url_for

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
    return "Hello World"

# add for future login (for chatting with ai)
@app.route('/login')
def login():
    return "login here"

if __name__ == "__main__":
    app.run(debug=False)