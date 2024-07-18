import os
import time
import io_ops as io
import streamlit as st
import features as ft
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
os.environ['Google_API_KEY'] = os.getenv("GOOGLE_API_KEY")

st.title('Cobra.Ai')

llm = ChatGroq(groq_api_key=groq_api_key, model='llama3-8b-8192')

def vector_embedding():

    try:
        if imquery:
            return 
        
        if "vectors" not in st.session_state:
            st.session_state.embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001')
            st.session_state.loader = PyPDFDirectoryLoader("./files")
            st.session_state.docs = st.session_state.loader.load()
            st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            st.session_state.final_document = st.session_state.text_splitter.split_documents(st.session_state.docs)
            st.session_state.vectors = FAISS.from_documents(st.session_state.final_document, st.session_state.embeddings)
            st.success("Memorised Everything.", icon="✅")
    
    except:
        pass

def clndir(d = './files/'):
    
    try: 
        for file in os.listdir(d):
            os.remove(os.path.join(d, file))

        st.success("All files were deleted.")

    except Exception as e:
        print(f'Error {e}')

def download_file(query, file_path="output.txt"):
    
    io.main()
    with open("output.pdf", "rb") as f:
        data = f.read()

    st.download_button(
        label = "Download",
        data = data,
        file_name = query + " - CobraAi.pdf",
        mime = "text/plain",
    )

docs = st.file_uploader(label="Upload Document", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

preview = st.checkbox("Preview")

prompt = ChatPromptTemplate.from_template(
    '''
    You are cobra.ai, a helpful assistant that only answers questions based on the provided context. 
    Your responeses are most accurate for the asked question.
    Your name: CoBRA.
    Your description: COBRA (Content-Based Retrieval and Analysis) is an AI-powered system designed
    to process images or PDF documents using langchain framework with Groq inference. 
    It efficiently retrieves and analyzes content from diverse sources, enabling rapid and 
    accurate information extraction for various applications. It internally calls Llama 3 for generating text reponses
    and gemini-pro-vision to analyse images. Cobra.Ai is created by Akshat Sanghvi.
    Your Github repository - https://github.com/iiakshat/cobra.ai
    Akshat's Linkedin profile - https://www.linkedin.com/in/akshat-sanghvi/
    Akshat's Github profile - https://github.com/iiakshat

    Context:<context>
    {context} <context>
    Question: {input} 
    ''') 

prompt2 = ChatPromptTemplate.from_template(
    """You are given with responses generated by a model
    for every image when multiple were given to it and was asked query : {input}
    Your task it to combine all the responses into one final response that answers the query.
    Do not tell if you combined any response. Your output should be a final response without any additional text.
    <context> {context} <context>
    """)

if preview:
    ft.display(docs)

if docs:
    if docs[0].name.endswith(".pdf"):
        for doc in docs:
            if doc.name.endswith(".pdf"):
                with open(os.path.join("files",doc.name),"wb") as f:
                    f.write(doc.getbuffer())

        st.success(f"Success: Saved {len(docs)} file(s).", icon="✅")

        imquery = st.checkbox("My query is related to only images in the pdf.")
        query = st.text_input("Question", placeholder="Ask Me Anything From PDF.")


        if imquery:
            try:
                if preview:
                    ft.display(docs, imquery)

                images = ft.details(docs)
                com_response = "\n".join(ft.get_response(images=images, query=query))

                chain = prompt2 | llm
                s = time.perf_counter()
                response = chain.invoke({'input': query, 'context': com_response})

                if query:
                    res = dict(response)["content"]
                    st.write(res)
                    io.write_to_file(query, res)
                    f = time.perf_counter()
                    st.divider()
                    st.caption(f"Time taken : {round(f-s,2)} seconds")
                    download_file(query)
                
                clndir()

            except Exception as e:
                print("Error : ",e)

        else:
            vector_embedding()
            clndir()

            if query and not imquery:
                s = time.perf_counter()
                document_Chain = create_stuff_documents_chain(llm, prompt)
                retriever = st.session_state.vectors.as_retriever()
                retireval_Chain = create_retrieval_chain(retriever, document_Chain)

                response = retireval_Chain.invoke({'input':query})
                res = response['answer']
                st.write(res)
                f = time.perf_counter()
                st.divider()
                st.caption(f"Time taken : {round(f-s,2)} seconds")
                io.write_to_file(query, res)
                download_file(query)

    else:
        try:
            images = ft.details(docs)
            query = st.text_input("Question", placeholder="Ask Me About Image(s)")
            com_response = "\n".join(ft.get_response(images=images, query=query))

            chain = prompt2 | llm
            s = time.perf_counter()
            response = chain.invoke({'input': query, 'context': com_response})
            if query:
                res = dict(response)["content"]
                st.write(res)
                f = time.perf_counter()
                st.divider()
                st.caption(f"Time taken : {round(f-s,2)} seconds")
                io.write_to_file(query, res)
                download_file(query)

        except Exception as e:
            st.error(f"Error: {e} \n\n Try Changing the input.", icon="🚨")
            print(e)
