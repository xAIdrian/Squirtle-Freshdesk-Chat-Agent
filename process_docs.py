# save this as `process_docs.py`
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
import os

def create_faiss_index():
    embeddings = OpenAIEmbeddings(
        openai_api_key="test"
    )
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    docs = []
    for file in os.listdir("docs"):
        if file.endswith(".txt"):
            loader = TextLoader(os.path.join("docs", file))
            docs.extend(text_splitter.split_documents(loader.load()))

    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local("faiss_index")
    print("FAISS index created and saved to 'faiss_index'")

if __name__ == "__main__":
    create_faiss_index()
