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


def process_question(question, image_only, llm, prompt):
    
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
    fmt = ""
    question = request.form.get("question")
    preview_images = request.form.get('previewimage', 'false').lower() == 'true'
    image_only = request.form.get("imagequery", 'false').lower() == 'true'
    
    image_data = ft.display(files, preview_images, streamlit=False)  
    socketio.emit('display_images', {'images': image_data})
    
    if not files:
        files = request.files.getlist('file')
        if not files or not question:
            return jsonify({'error': 'Both files and question are required.'}), 400

        nfiles = len(files)
        
        for files in os.listdir(app.config['UPLOAD_FOLDER']):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], files))
        
        os.rmdir(app.config['UPLOAD_FOLDER'])
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        for i, file in enumerate(files):
            fmt = file.filename.split('.')[-1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file.filename}")
            
            if file:
                print(f"Saving file {file.filename} to {file_path}")
                file.save(file_path)
                saved_size = os.path.getsize(file_path)
                print(f"File {file.filename} saved with size {saved_size} bytes.")
                if saved_size == 0:
                    print(f"Warning: File {file.filename} is empty after saving.")
                socketio.emit('progress', {'message': f"File {i+1} of {nfiles} saved."})
            else:
                print(f"Warning: File object {file.filename} is empty.")

        vectors_ = vector_embedding(flask=True)

    file_cnt = 0
    if not vectors_:
        socketio.emit('progress', {'message': "Waiting for files..."})
    while not vectors_:
        time.sleep(0.5)
        file_cnt += 1
        if file_cnt == 20:
            return "Either None Or Too Many Files Have Been Uploaded."

    if fmt in ["mp3", "mp4", "wav"]:
        pass
    
    answer, restime = process_question(question, image_only, llm, prompt)
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], f))

    socketio.emit('answer_response', {'answer': answer, 'response_time': round(restime, 2)})
    return '', 204  # No content response to avoid re-rendering


@socketio.on('message')
def handle_message(message):
    send(message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True, port=8000)
