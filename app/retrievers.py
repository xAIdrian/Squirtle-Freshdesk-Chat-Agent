from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.callbacks.base import BaseCallbackHandler
from langchain.vectorstores import Pinecone
from pinecone import ServerlessSpec
from langchain.docstore.document import Document
from typing import List, Dict
import streamlit as st
import tempfile
import json
import os
import time

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

api_key = os.environ.get("PINECONE_API_KEY")
openai_api_key = os.environ.get('OPENAI_API_KEY') or 'OPENAI_API_KEY'
index_name = 'langchain-retrieval-agent-fast'
model_name = 'text-embedding-ada-002'

# configure client
pc = Pinecone(api_key=api_key)
cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
region = os.environ.get('PINECONE_REGION') or 'us-east-1'

spec = ServerlessSpec(cloud=cloud, region=region)

if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)

# we create a new index if one has not been created already
# if index_name not in pc.list_indexes().names():
pc.create_index(
    index_name,
    dimension=1536,  # dimensionality of text-embedding-ada-002
    metric='dotproduct',
    spec=spec
)

# wait for index to be initialized
while not pc.describe_index(index_name).status['ready']:
    time.sleep(1)
    
index = pc.Index(index_name)

print("🚀 Index created successfully")
print(index.describe_index_stats())

def json_to_documents(json_data: List[Dict]) -> List[Document]:
    """Convert JSON data to Document objects for embedding"""
    documents = []
    for item in json_data:
        # Extract the text content you want to embed
        # Adjust these fields based on your JSON structure
        content = f"""
        Subject: {item.get('subject', '')}
        Description: {item.get('description', '')}
        Status: {item.get('status', '')}
        Priority: {item.get('priority', '')}
        """
        
        # Create metadata from other relevant fields
        metadata = {
            'ticket_id': item.get('id'),
            'created_at': item.get('created_at'),
            'status': item.get('status'),
            'priority': item.get('priority'),
            # Add any other metadata fields you want to preserve
        }
        
        doc = Document(
            page_content=content.strip(),
            metadata=metadata
        )
        documents.append(doc)
    
    return documents

@st.cache_resource
def configure_retriever_from_json(json_data: List[Dict]):
    """Configure retriever from JSON data"""
    
    # Convert JSON to documents
    docs = json_to_documents(json_data)

    # Split documents if they're too long
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=30000,
        chunk_overlap=2000,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(docs)

    embed = OpenAIEmbeddings(
        model=model_name,
        openai_api_key=openai_api_key
    )

    # Define retriever
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 4})

    return retriever

if __name__ == "__main__":
    query = "when was the college of engineering in the University of Notre Dame established?"

    # vectorstore.similarity_search(
    #     query,  # our search query
    #     k=3  # return 3 most relevant docs
    # )
