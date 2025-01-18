from openai import OpenAI
import streamlit as st
from consts import INSTRUCTIONS, PRE_PROMPT

openaiClient = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

def retrieve_assistant(assistant_id):
    try:
        return openaiClient.beta.assistants.retrieve(assistant_id)
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:12 ~ e:', e);
        return None

def list_assistants():
    try:
        assistants = openaiClient.beta.assistants.list()
        print('🚀 ~ file: ottobot_core.py:15 ~ assistants:', assistants);
        return assistants
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:17 ~ e:', e);
        return None

def create_assistant(name, tools, model):
    try:
      assistant = openaiClient.beta.assistants.create(
          name=name,
          instructions=INSTRUCTIONS,
          tools=tools,
          model=model,
      )
      print('🚀 ~ file: ottobot_core.py:26 ~ assistant:', assistant);
      return assistant
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:28 ~ e:', e);
        return None
    
def create_vector_store_file(vectorstore_id, file_path):
    try:
        vector_store_file = openaiClient.beta.vector_stores.files.create(
            vector_store_id=vectorstore_id,
            file_id=file_path
        )
        return vector_store_file
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:32 ~ e:', e);
        return None

def upload_vector_store_files_batch(vectorstore_id, file_paths):
    try:
        file_ids = []
        for file_path in file_paths:
            file_ids.append(create_vector_store_file(vectorstore_id, file_path).id)

        vector_store_file_batch = openaiClient.beta.vector_stores.file_batches.create(
            vector_store_id=vectorstore_id,
            file_ids=file_ids
        )
        return vector_store_file_batch
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:46 ~ e:', e);
        return None

def get_or_create_vector_store(assistant_id):
    """Retrieve or create the vector store for the assistant."""
    try:
        assistant = openaiClient.beta.assistants.retrieve(assistant_id)

        # Check if vector store already exists
        if assistant.tool_resources.file_search.vector_store_ids:
            first_vector_store_id = assistant.tool_resources.file_search.vector_store_ids[0]
            if first_vector_store_id:
                print('🚀 ~ file: ottobot_core.py:61 ~ first_vector_store_id:', first_vector_store_id);
                return openaiClient.beta.vector_stores.retrieve(vector_store_id=first_vector_store_id)

        # Create a new vector store
        vector_store = openaiClient.beta.vector_stores.create(name="ottobot-vector-store")
        print('🚀 ~ file: ottobot_core.py:65 ~ vector_store:', vector_store);

        openaiClient.beta.assistants.update(
            assistant_id, 
            tool_resources={
                "file_search": {"vector_store_ids": [vector_store.id]}
            }
        )
        print('🚀 ~ file: ottobot_core.py:78 ~ assistant:', assistant);

        return vector_store
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:86 ~ e:', e);
        return None

def retrieve_vector_store(vectorstore_id):
    try:
        vector_store = openaiClient.beta.vector_stores.retrieve(vector_store_id=vectorstore_id)
        print('🚀 ~ file: ottobot_core.py:96 ~ vector_store:', vector_store);
        return vector_store
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:99 ~ e:', e);
        return None

def upload_vector_store_files_batch(vectorstore_id, file_paths):
    vector_store = retrieve_vector_store(vectorstore_id)
    if not vector_store or not vector_store.file_counts:
        print('🚀 ~ file: ottobot_core.py:103 ~ vector_store:', vector_store);
        return None
    if vector_store.file_counts.total > 0:
        print('🚀 ~ file: ottobot_core.py:103 ~ vector_store:', vector_store);
        return None

    file_ids = []
    for file_path in file_paths:
        try:
            # First upload the file to OpenAI
            with open(file_path, 'rb') as file:
                uploaded_file = openaiClient.files.create(
                    file=file,
                    purpose="assistants"
                )
            
            # Then create the vector store file
            vector_store_file = openaiClient.beta.vector_stores.files.create(
                vector_store_id=vectorstore_id,
                file_id=uploaded_file.id
            )
            file_ids.append(vector_store_file.id)
            print('🚀 ~ file: ottobot_core.py:127 ~ file_ids:', file_ids);
        except FileNotFoundError:
            print('🚀 ~ file: ottobot_core.py:129 ~ FileNotFoundError:', FileNotFoundError);
        except Exception as e:
            print('🚀 ~ file: ottobot_core.py:131 ~ e:', e);

    if not file_ids:
        print('🚀 ~ file: ottobot_core.py:135 ~ No files uploaded');
        return None

    vector_store_file_batch = openaiClient.beta.vector_stores.file_batches.create(
        vector_store_id=vectorstore_id,
        file_ids=file_ids
    )
    print('🚀 ~ file: ottobot_core.py:141 ~ vector_store_file_batch:', vector_store_file_batch);
    return vector_store_file_batch

def delete_file_from_vector_store(assistant_id, file_id):
    try:
        vector_store_id = get_or_create_vector_store(assistant_id)
        openaiClient.beta.vector_stores.files.delete(vector_store_id, file_id)
        print('🚀 ~ file: ottobot_core.py:148 ~ file_id:', file_id);
        return file_id
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:150 ~ e:', e);
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
    try:
        thread = openaiClient.beta.threads.retrieve(thread_id)
        return thread
    except Exception as e:
        print(f"Error retrieving thread: {e}")
        return None

def delete_thread(thread_id):
    try:
        openaiClient.beta.threads.delete(thread_id)
        return thread_id
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:189 ~ e:', e);
        return None

def add_message_to_thread(thread_id, message):
    try:
        openaiClient.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )
        return message
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:201 ~ e:', e);
        return None

def list_messages_in_thread(thread_id):
    try:
        messages = openaiClient.beta.threads.messages.list(thread_id)
        return messages
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:209 ~ e:', e);
        return None

def retrieve_single_message_from_thread(thread_id, message_id):
    try:
        message = openaiClient.beta.threads.messages.retrieve(thread_id, message_id)
        return message
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:217 ~ e:', e);
        return None

def delete_message_from_thread(thread_id, message_id):
    try:
        openaiClient.beta.threads.messages.delete(thread_id, message_id)
        return message_id
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:225 ~ e:', e);
        return None

def run_assistant(assistant_id, thread_id):
    try:
        run = openaiClient.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
            stream=True
        )
        return run
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:237 ~ e:', e);
        return None

def create_thread_and_run_assistant(assistant_id, message):
    try:
        run = openaiClient.beta.threads.create_and_run(
            assistant_id=assistant_id,
            instructions=PRE_PROMPT + message,
            stream=True
        )
        return run
    except Exception as e:
        print('🚀 ~ file: ottobot_core.py:249 ~ e:', e);
        return None

