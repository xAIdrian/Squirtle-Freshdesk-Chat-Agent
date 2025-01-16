from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

openai = OpenAI()

def create_assistant(name, instructions, tools, model):
    try:
      assistant = openai.beta.assistants.create(
          name=name,
          instructions=instructions,
          tools=[
            {
              "type": "code_interpreter"
            },
            {
              "type": "file_search"
            }
          ],
          model="gpt-4o",
      )
      return assistant
    except Exception as e:
        print(f"Error creating assistant: {e}")
        return None

def get_or_create_vector_store(assistant_id):
    """Retrieve or create the vector store for the assistant."""
    try:
        assistant = openai.Assistant.retrieve(assistant_id)

        # Check if vector store already exists
        if "file_search" in assistant.tool_resources and assistant.tool_resources["file_search"]["vector_store_ids"]:
            return assistant.tool_resources["file_search"]["vector_store_ids"][0]

        # Create a new vector store
        vector_store = openai.VectorStore.create({"name": "fitness-assistant-vector-store"})
        openai.Assistant.update(assistant_id, {
            "tool_resources": {
                "file_search": {"vector_store_ids": [vector_store["id"]]}
            }
        })
        return vector_store["id"]
    except Exception as e:
        print(f"Error retrieving assistant: {e}")
        return None

def upload_file_to_vector_store(assistant_id, file_path):
    try:
        # Upload file to assistant's vector store
        vector_store_id = get_or_create_vector_store(assistant_id)
        openai_file = openai.File.create({
            "file": file_path,
            "purpose": "assistants"
        })
        openai.VectorStoreFile.create(vector_store_id, {
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
        openai.VectorStoreFile.delete(vector_store_id, file_id)
        print(f"File deleted from vector store successfully! File ID: {file_id}")
        return file_id
    except Exception as e:
        print(f"Error deleting file: {e}")
        return None

def list_files_in_vector_store(assistant_id):
    try:
        vector_store_id = get_or_create_vector_store(assistant_id)
        file_list = openai.VectorStoreFile.list(vector_store_id)
        files = []
        for file in file_list["data"]:
            file_details = openai.File.retrieve(file["id"])
            vector_file_details = openai.VectorStoreFile.retrieve(vector_store_id, file["id"])
            files.append({
                "file_id": file["id"],
                "filename": file_details["filename"],
                "status": vector_file_details["status"]
            })
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []
