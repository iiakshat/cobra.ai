import os
from io import BytesIO
import base64
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send
from streamlitapp import *

load_dotenv()
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

groq_api_key = os.getenv("GROQ_API_KEY")
Google_API_KEY = os.getenv("GOOGLE_API_KEY")
UPLOAD_FOLDER = './files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
vectors_ = None 
files = None

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/home', methods=['POST'])
def home():
    api_key = request.form.get('api_key', Google_API_KEY)
    name = request.form['name']
    return render_template('home.html', name=name, api_key=api_key)

@socketio.on('upload_files')
def handle_file_upload():
    files = request.files.getlist('file')
    imquery = request.form.get('previewimage', 'false').lower() == 'true'
    image_data = ft.display(files, imquery)
    
    socketio.emit('display_images', {'images': image_data})


def process_question(question, image_only):
    
    # if question and not image_only:

    if question and vectors_:

        s = time.perf_counter()

        document_Chain = create_stuff_documents_chain(llm, prompt)
        retriever = vectors_.as_retriever()
        retireval_Chain = create_retrieval_chain(retriever, document_Chain)
        response = retireval_Chain.invoke({'input':question})
        res = response['answer']
        io_ops.write_to_file(question, res)
        f = time.perf_counter()

        return [res, f-s]

@app.route('/query', methods=['POST'])
def upload_files():

    global files, vectors_
    question = request.form.get("question")
    preview_images = request.form.get("previewimage")
    image_only = request.form.get("imagequery")


    if not files:
        files = request.files.getlist('file')

        if not files or not question:
            return jsonify({'error': 'Both files and question are required.'}), 400

        nfiles = len(files)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        for i, file in enumerate(files):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp-{i+1}.pdf")
            file.save(file_path)
            socketio.emit('progress', {'message': f"File {i+1} of {nfiles} saved."})
            print(f"File {i+1} of {nfiles} saved.")

        vectors_ = vector_embedding(flask=True)

    i=0
    while not vectors_:
        socketio.emit('progress', {'message': "Waiting for files..."})
        time.sleep(0.5)
        i+=1
        if i>100:
            return "Either None Or Too Many Files Have Been Uploaded."

    answer, restime = process_question(question, image_only)
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))

    return jsonify({'answer': answer, "response_time": round(restime,2)})

@socketio.on('message')
def handle_message(message):
    send(message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)
