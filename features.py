from dotenv import load_dotenv
import os
from io import BytesIO
import streamlit as st
from PIL import Image
from pdf2image import convert_from_bytes
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro-vision')

context_prompt = """
You are an expert in understanding every type of image. We will upload multiple images of anything,
including handwritten notes, diagrams, or other content. You will be asked questions regarding the details 
that these images contain, and you have to answer those questions by considering the context of all provided images.
"""

def get_response(images, query, prompt=context_prompt):
    responses = []
    for image in images:
        response = model.generate_content([prompt, image, query])
        responses.append(response.text)
        
    return responses

def details(uploaded_files):
    image_parts = []
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":

                pdf_bytes = uploaded_file.read()
                images = convert_from_bytes(pdf_bytes)

                print(len(images))
                for image in images:
                    img_bytes = BytesIO()
                    image.save(img_bytes, format='PNG')

                    print("Images saved")
                    image_parts.append({
                        "mime_type": "image/png",
                        "data": img_bytes.getvalue()
                    })

            else:
                image_parts.append({
                    "mime_type": uploaded_file.type,
                    "data": uploaded_file.getvalue()
                })

    return image_parts

def display(files):
    images = []
    if files:
        for uploaded_file in files:

            if uploaded_file.type == "application/pdf":
                pdf_images = convert_from_bytes(uploaded_file.read())
                images.extend(pdf_images)

            else:
                image = Image.open(uploaded_file)
                images.append(image)

    if images:
        cols = st.columns(len(images))
        for col, image in zip(cols, images):
            col.image(image, caption="Uploaded Image", width=250)
