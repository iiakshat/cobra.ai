import os
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

prompt = ChatPromptTemplate.from_template(
    '''You are a helpful assistant that only answers questions based on the provided context. 
    Your responeses are most accurate for the asked question. <context>
    {context} <context>
    Question: {input} ''')

prompt2 = ChatPromptTemplate.from_template(
    """You are given with responses generated by a model
    for every image when multiple were given to it and was asked query : {input}
    Your task it to combine all the responses into one final response that answers the query.
    Do not tell if you combined any response. Your output should be a final response without any additional text.
    <context> {context} <context>
    """)

def vector_embedding():

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

def clndir(d = './files/'):
    
    try: 
        for file in os.listdir(d):
            os.remove(os.path.join(d, file))

        st.success("All files were deleted.")

    except Exception as e:
        print(f'Error {e}')

docs = st.file_uploader(label="Upload Document", type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True)

preview = st.checkbox("Preview")

if preview:
    ft.display(docs)

if docs:
    if docs[0].name.endswith(".pdf"):
        for doc in docs:
            if doc.name.endswith(".pdf"):
                with open(os.path.join("files",doc.name),"wb") as f:
                    f.write(doc.getbuffer())

        st.success(f"Success: Saved {len(docs)} file(s).", icon="✅")

        imquery = st.checkbox("My query is related to images in the pdf.")
        query = st.text_input("Question", placeholder="Ask Me Anything From PDF.")

        if imquery:
            try:
                print("Uploaded FIles: ", len(docs))
                images = ft.details(docs)

                print("Data extracted")
                com_response = "\n".join(ft.get_response(images=images, query=query))
                
                print("Response received")

                chain = prompt2 | llm

                print("Invoking Chain")
                response = chain.invoke({'input': query, 'context': com_response})
                if query:
                    print("AI Resposne")
                    st.write(dict(response)["content"])
                
                clndir()

            except Exception as e:
                print("Error : ",e)

        else:
            print("Running Because No PDFs")
            vector_embedding()
            clndir()

            if query and not imquery:
                document_Chain = create_stuff_documents_chain(llm, prompt)
                retriever = st.session_state.vectors.as_retriever()
                retireval_Chain = create_retrieval_chain(retriever, document_Chain)

                response = retireval_Chain.invoke({'input':query})
                st.write(response['answer'])

    else:
        try:

            images = ft.details(docs)
            query = st.text_input("Question", placeholder="Ask Me About Image(s)")
            com_response = "\n".join(ft.get_response(images=images, query=query))

            chain = prompt2 | llm
            response = chain.invoke({'input': query, 'context': com_response})
            if query:
                st.write(dict(response)["content"])

        except Exception as e:
            st.error(f"Unknown Format", icon="🚨")
            print(e)
