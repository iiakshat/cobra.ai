import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO

load_dotenv()
app = Flask(__name__)

groq_api_key = os.getenv("GROQ_API_KEY")
os.environ['Google_API_KEY'] = os.getenv("GOOGLE_API_KEY")

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login')
def auth():
    api_key = request.form['api_key']
    name = request.form['name']
    print(api_key, name)
    return redirect(url_for('home.html', name=name, api_key=api_key))

@app.route('/home')
def home():
    name = request.args.get('name', 'User')
    return render_template('home.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)