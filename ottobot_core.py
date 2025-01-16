from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler
import streamlit as st
openaiClient = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

def retrieve_assistant(assistant_id):
    return openaiClient.beta.assistants.retrieve(assistant_id)

def list_assistants():
    assistants = openaiClient.beta.assistants.list()
    print(f"Assistants: {assistants}")
    return assistants

def create_assistant(name, instructions, tools, model):
    try:
      assistant = openaiClient.beta.assistants.create(
          name=name,
          instructions=instructions,
          tools=tools,
          model=model,
      )
      print(f"Assistant created: {assistant}")
      return assistant
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None
    
def create_vector_store_file(vectorstore_id, file_path):
    vector_store_file = openaiClient.beta.vector_stores.files.create(
        vector_store_id=vectorstore_id,
        file_id=file_path
    )
    return vector_store_file

def upload_vector_store_files_batch(vectorstore_id, file_paths):
    file_ids = []
    for file_path in file_paths:
        file_ids.append(create_vector_store_file(vectorstore_id, file_path).id)

    vector_store_file_batch = openaiClient.beta.vector_stores.file_batches.create(
        vector_store_id=vectorstore_id,
        file_ids=file_ids
    )
    return vector_store_file_batch

def get_or_create_vector_store(assistant_id):
    """Retrieve or create the vector store for the assistant."""
    # try:
    assistant = openaiClient.beta.assistants.retrieve(assistant_id)

    # Check if vector store already exists
    first_vector_store_id = assistant.tool_resources.file_search.vector_store_ids[0]
    if first_vector_store_id:
        print(f"Vector store already exists: {first_vector_store_id}")
        return openaiClient.beta.vector_stores.retrieve(vector_store_id=first_vector_store_id)

    # Create a new vector store
    vector_store = openaiClient.beta.vector_stores.create(name="ottobot-vector-store")
    print(f"Vector store created: {vector_store}")
    openaiClient.beta.assistants.update(
        assistant_id, 
        tool_resources={
            "file_search": {"vector_store_ids": [vector_store.id]}
        }
    )
    print(f"Assistant updated with vector store: {assistant}")

    return vector_store
    # except Exception as e:
    #     print(f"Error retrieving assistant: {e}")
    #     return None

def upload_file_to_vector_store(assistant_id, file_path):
    try:
        # Upload file to assistant's vector store
        vector_store_id = get_or_create_vector_store(assistant_id)
        openai_file = openaiClient.beta.files.create({
            "file": file_path,
            "purpose": "assistants"
        })
        openaiClient.beta.vector_stores.files.create(vector_store_id, {
            "file_id": openai_file["id"]
        })
        print(f"File uploaded to vector store successfully! File ID: {openai_file['id']}")
        return openai_file["id"]
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

def delete_file_from_vector_store(assistant_id, file_id):
    try:
        vector_store_id = get_or_create_vector_store(assistant_id)
        openaiClient.beta.vector_stores.files.delete(vector_store_id, file_id)
        print(f"File deleted from vector store successfully! File ID: {file_id}")
        return file_id
    except Exception as e:
        print(f"Error deleting file: {e}")
        return None

def list_files_in_vector_store(assistant_id):
    try:
        vector_store_id = get_or_create_vector_store(assistant_id)
        file_list = openaiClient.beta.vector_stores.files.list(vector_store_id)
        files = []
        for file in file_list["data"]:
            file_details = openaiClient.beta.files.retrieve(file["id"])
            vector_file_details = openaiClient.beta.vector_stores.files.retrieve(vector_store_id, file["id"])
            files.append({
                "file_id": file["id"],
                "filename": file_details["filename"],
                "status": vector_file_details["status"]
            })
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def create_thread():
    thread = openaiClient.beta.threads.create()
    return thread

def retrieve_thread(thread_id):
    thread = openaiClient.beta.threads.retrieve(thread_id)
    return thread

def delete_thread(thread_id):
    openaiClient.beta.threads.delete(thread_id)
    return thread_id

def add_message_to_thread(thread_id, message):
    openaiClient.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )

def list_messages_in_thread(thread_id):
    messages = openaiClient.beta.threads.messages.list(thread_id)
    return messages

def retrieve_message_from_thread(thread_id, message_id):
    message = openaiClient.beta.threads.messages.retrieve(thread_id, message_id)
    return message

def delete_message_from_thread(thread_id, message_id):
    openaiClient.beta.threads.messages.delete(thread_id, message_id)
    return message_id

def run_assistant(assistant_id, thread_id, message):
    run = openaiClient.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=message,
        stream=True
    )
    return run

def create_thread_and_run_assistant(assistant_id, message):
    run = openaiClient.beta.threads.create_and_run(
        assistant_id=assistant_id,
        instructions=message,
        stream=True
    )
    return run
