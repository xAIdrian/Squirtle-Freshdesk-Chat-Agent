import streamlit as st
import openai
import pandas as pd
import json

# Set up OpenAI API Key
openai.api_key = st.secrets["openai_api_key"]

# Constants
assistant_id = "your-assistant-id"  # Replace with your Assistant ID

# Streamlit App Title
st.title("Fitness Assistant Chatbot with File Management")

# Sidebar Configuration
st.sidebar.header("Chat Settings")
model = st.sidebar.selectbox("Model", ["gpt-3.5-turbo", "gpt-4"])
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)

# Helper Functions
def get_or_create_vector_store():
    """Retrieve or create the vector store for the assistant."""
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

# File Upload and Vector Store Integration
st.sidebar.header("Manage Files in Vector Store")
uploaded_file = st.sidebar.file_uploader("Upload a file (CSV or JSON)", type=["csv", "json"])

if uploaded_file:
    try:
        # Upload file to assistant's vector store
        vector_store_id = get_or_create_vector_store()
        openai_file = openai.File.create({
            "file": uploaded_file,
            "purpose": "assistants"
        })
        openai.VectorStoreFile.create(vector_store_id, {
            "file_id": openai_file["id"]
        })
        st.sidebar.success("File uploaded to vector store successfully!")
    except Exception as e:
        st.sidebar.error(f"Error uploading file: {e}")

# List Files in Vector Store
if st.sidebar.button("List Files"):
    try:
        vector_store_id = get_or_create_vector_store()
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
        st.sidebar.json(files)
    except Exception as e:
        st.sidebar.error(f"Error listing files: {e}")

# Delete File from Vector Store
file_id_to_delete = st.sidebar.text_input("File ID to Delete", "")
if st.sidebar.button("Delete File"):
    try:
        vector_store_id = get_or_create_vector_store()
        openai.VectorStoreFile.delete(vector_store_id, file_id_to_delete)
        st.sidebar.success("File deleted successfully!")
    except Exception as e:
        st.sidebar.error(f"Error deleting file: {e}")

# Chat Input and Response
st.subheader("Chat with the Fitness Assistant")
user_input = st.text_input("You:", placeholder="Ask your fitness-related question...")

if st.button("Send"):
    if user_input.strip():
        messages = [
            {"role": "system", "content": "You are a fitness assistant. Provide accurate and helpful fitness information."},
            {"role": "user", "content": user_input}
        ]

        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature
            )
            reply = response["choices"][0]["message"]["content"]

            # Display Assistant Response
            st.markdown(f"**Assistant:** {reply}")

            # Output JSON
            output_json = {"user_query": user_input, "assistant_reply": reply}
            st.subheader("JSON Output")
            st.json(output_json)

            # Display JSON as DataFrame
            st.subheader("Output DataFrame")
            output_df = pd.DataFrame([output_json])
            st.dataframe(output_df)

        except Exception as e:
            st.error(f"Error with OpenAI API: {e}")
    else:
        st.warning("Please enter a question.")
