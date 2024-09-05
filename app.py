import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send

load_dotenv()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

groq_api_key = os.getenv("GROQ_API_KEY")
Google_API_KEY = os.getenv("GOOGLE_API_KEY")
data = ""

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home', methods=['POST'])
def home():
    api_key = request.form.get('api_key', Google_API_KEY)
    name = request.form['name']
    return render_template('home.html', name=name, api_key=api_key)

@app.route('/upload_files', methods=['POST'])
def upload_files():
    files = request.files.getlist('files[]')
    global data
    data = vectorEmbedding(files)
    if data:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 500
    

@app.route('/send_question', methods=['POST'])
def send_question():
    data = request.get_json()
    question = data['question']
    preview_images = data['preview_images']
    image_only = data['image_only']
    
    answer = process_question(question, preview_images, image_only)
    return jsonify(answer)

def process_question(question, preview_images, image_only):
    # Your logic to generate an answer based on the uploaded files
    return "Sample answer based on the uploaded files"

@socketio.on('message')
def handle_message(message):
    send(message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='localhost')
