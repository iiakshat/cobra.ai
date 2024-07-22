import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO

load_dotenv()
app = Flask(__name__)

groq_api_key = os.getenv("GROQ_API_KEY")
Google_API_KEY = os.getenv("GOOGLE_API_KEY")

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home', methods=['POST'])
def home():
    api_key = request.form.get('api_key', Google_API_KEY)
    name = request.form['name']
    return render_template('home.html', name=name, api_key=api_key)

@app.route('/send_question', methods=['POST'])
def send_question():
    data = request.get_json()
    question = data['question']
    preview_images = data['preview_images']
    image_only = data['image_only']
    

    answer = f"Question received: {question}"
    
    # Return the answer
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)