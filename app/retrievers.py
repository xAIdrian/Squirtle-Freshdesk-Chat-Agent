from langchain.vectorstores import DocArrayInMemorySearch
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.base import BaseCallbackHandler
from langchain.document_loaders import PyPDFLoader
import os
import tempfile
import streamlit as st
from handlers import StaticFile

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the 'docs' folder
pdf_dir = os.path.join(script_dir, 'docs')

# Check if the directory exists
if not os.path.exists(pdf_dir):
    print(f"Directory not found: {pdf_dir}")

@st.cache_resource
def configure_retriever(_uploaded_files):
    # Read documents
    docs = []
    temp_dir = tempfile.TemporaryDirectory()
    for file in _uploaded_files:
        temp_filepath = os.path.join(temp_dir.name, file.name)
        with open(temp_filepath, "wb") as f:
            f.write(file.getvalue())
        loader = PyPDFLoader(temp_filepath)
        docs.extend(loader.load())

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # Create embeddings and store in vectordb
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = DocArrayInMemorySearch.from_documents(splits, embeddings)

    # Define retriever
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 4})

    return retriever

def get_static_files():
    static_files = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(pdf_dir, filename)
            static_files.append(StaticFile(file_path))
    
    return static_files
