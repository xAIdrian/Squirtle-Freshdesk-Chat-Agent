from typing import List, Dict
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))


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
