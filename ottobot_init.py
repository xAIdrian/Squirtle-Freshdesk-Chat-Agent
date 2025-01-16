from openai import OpenAI
from ottobot_core import list_assistants, create_assistant, retrieve_assistant, get_or_create_vector_store

def create_new_assistant_if_not_exists(name):
    assistants = list_assistants()

    # Check if assistant with given name exists
    existing_assistant = None
    for assistant in assistants.data:
        if assistant.name == name:
            existing_assistant = retrieve_assistant(assistant.id)
            break
    
    if existing_assistant:
        print(f"Assistant {name} already exists")
        return existing_assistant
    else:
        print(f"Assistant {name} does not exist, creating new one")
        return create_assistant(
            name=name,
            instructions="ottobot",
            tools=[
                {
                    "type": "file_search"
                },
                {
                    "type": "code_interpreter"
                }
            ],
            model="gpt-4o"
        )

def create_new_ottobot_with_files(name, files):
    assistant = create_new_assistant_if_not_exists(name)
    vector_store = get_or_create_vector_store(assistant.id)
    for file in files:
        vector_store.add_documents(file)
    return assistant
