from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain.docstore.document import Document
from typing import List, Dict
import os
import time
from batch_tickets import FreshdeskBatchFetcher

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
        content = f"""
        Subject: {item.get('subject', '')}
        Description: {item.get('description', '')}
        Description Text: {item.get('description_text', '')}
        """
        
        # Create metadata from other relevant fields
        metadata = {
            'ticket_id': item.get('id'),
            'created_at': item.get('created_at'),
            'status': item.get('status'),
            'priority': item.get('priority'),
        }
        
        doc = Document(
            page_content=content.strip(),
            metadata=metadata
        )
        documents.append(doc)
    
    return documents

def upload_to_pinecone(json_data: List[Dict]):
    """Upload JSON data to Pinecone and return the index"""
    # Convert JSON to documents
    docs = json_to_documents(json_data)

    # Split documents if needed
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=30000,
        chunk_overlap=2000,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(docs)

    # Create embeddings
    embeddings = OpenAIEmbeddings(
        model=model_name,
        openai_api_key=openai_api_key
    )
    
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    
    print("🚀 Data uploaded successfully")
    return vector_store

def test_pinecone_data():
    """Test that data is properly stored in Pinecone"""
    # Get index statistics
    stats = index.describe_index_stats()
    print(f"Total vectors in index: {stats['total_vector_count']}")
    
    # Test a sample query
    query = "high priority tickets"
    vectordb = Pinecone.from_existing_index(
        index_name=index_name,
        embedding=OpenAIEmbeddings()
    )
    
    results = vectordb.similarity_search(
        query,
        k=2  # Number of results to return
    )
    
    print("\nSample search results:")
    for doc in results:
        print(f"\nContent: {doc.page_content}")
        print(f"Metadata: {doc.metadata}")

# @st.cache_resource
# def configure_retriever_from_json(json_data: List[Dict]):
#     """Configure retriever from JSON data"""
    
#     # Convert JSON to documents
#     docs = json_to_documents(json_data)

#     # Split documents if they're too long
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=30000,
#         chunk_overlap=2000,
#         separators=["\n\n", "\n", " ", ""]
#     )
#     splits = text_splitter.split_documents(docs)

#     embed = OpenAIEmbeddings(
#         model=model_name,
#         openai_api_key=openai_api_key
#     )

#     # Define retriever
#     retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k": 2, "fetch_k": 4})

#     return retriever

if __name__ == "__main__":
    
    fetcher = FreshdeskBatchFetcher()
    tickets = fetcher.fetch_ticket_batch(page=1, per_page=100, limit=10)
    upload_to_pinecone(tickets)
