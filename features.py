from dotenv import load_dotenv
import os
import asyncio
import base64
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

async def generate_response(prompt, image, query):
    response = model.generate_content([prompt, image, query])
    return response.text

async def get_response_async(images, query, prompt=context_prompt):
    tasks = [generate_response(prompt, image, query) for image in images]
    responses = await asyncio.gather(*tasks)
    return responses

def get_response(images, query, prompt=context_prompt):
    try:
        return asyncio.run(get_response_async(images, query, prompt))
    except Exception as e:
        st.error(f"Error during async processing: {e}.")
        return []
    
def details(uploaded_files):
    image_parts = []
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":

                pdf_bytes = uploaded_file.read()
                images = convert_from_bytes(pdf_bytes)

                for image in images:
                    img_bytes = BytesIO()
                    image.save(img_bytes, format='PNG')

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

def display(files, imquery=False, streamlit=True):
    
    images = []
    if streamlit:
        if files:
            for uploaded_file in files:
                try:
                    if uploaded_file.type == "application/pdf":
                        pdf_images = convert_from_bytes(uploaded_file.read())
                        if imquery:
                            pdf_images = Image.open(uploaded_file)
                                
                        images.extend(pdf_images)

                    else:
                        image = Image.open(uploaded_file)
                        images.append(image)

                except:
                    st.error("Cannot Show Preview")

        max_images_per_row = 3
        if images:
            for i in range(0, len(images), max_images_per_row):
                row_images = images[i:i + max_images_per_row]
                cols = st.columns(len(row_images))
                for col, image in zip(cols, row_images):
                    col.image(image, caption="Uploaded Image", width=230)

    else:   
        for uploaded_file in files:
            try:
                if uploaded_file.mimetype == "application/pdf":
                    pdf_images = convert_from_bytes(uploaded_file.read())
                    if imquery:
                        pdf_images = [Image.open(uploaded_file)]
                    images.extend(pdf_images)
                else:
                    image = Image.open(uploaded_file)
                    images.append(image)
            except Exception as e:
                print(f"Error processing file: {e}")

        image_data = []
        for image in images:
            img_io = BytesIO()
            image.save(img_io, 'JPEG', quality=70)
            img_io.seek(0)
            img_base64 = base64.b64encode(img_io.getvalue()).decode('ascii')
            image_data.append(f"data:image/jpeg;base64,{img_base64}")

        return image_data