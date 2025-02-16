from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
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
def load_json_to_chroma(json_data, persist_directory="chroma_db"):
    # Convert JSON data to Document objects
    docs = []
    for item in json_data:
        doc = Document(
            page_content=str(item.get('content')),
            metadata=item.get('metadata', {})
        )
        docs.append(doc)

    # Split documents if needed
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # Create embeddings and store in ChromaDB using OpenAI
    embeddings = OpenAIEmbeddings()
    
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vectordb.persist()

    return vectordb.as_retriever(
        search_type="mmr", 
        search_kwargs={"k": 2, "fetch_k": 4}
    )

