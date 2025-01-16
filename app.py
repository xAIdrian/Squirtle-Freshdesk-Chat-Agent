
# app.py
import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.llms import OpenAI

# Load the FAISS index
def load_index():
    return FAISS.load_local("faiss_index", OpenAIEmbeddings(
        openai_api_key="test"
    ), allow_dangerous_deserialization=True)

def main():
    st.title("Continuous Chat with History")
    st.sidebar.header("Configuration")
    openai_api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
    
    if not openai_api_key:
        st.warning("Please enter your OpenAI API key to continue.")
        st.stop()

    # Initialize session state for chat history and memory
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "retriever" not in st.session_state:
        vector_store = load_index()
        st.session_state["retriever"] = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    if "qa_chain" not in st.session_state:
        st.session_state["qa_chain"] = ConversationalRetrievalChain.from_llm(
            OpenAI(temperature=0, openai_api_key=openai_api_key),
            retriever=st.session_state["retriever"]
        )

    # Chat UI
    st.subheader("Chat with Your Knowledge Base")
    user_question = st.text_input("Ask a question:", "")

    if st.button("Send"):
        if user_question.strip():
            with st.spinner("Generating response..."):
                qa_chain = st.session_state["qa_chain"]
                response = qa_chain({"question": user_question, "chat_history": st.session_state["chat_history"]})
                st.session_state["chat_history"].append((user_question, response["answer"]))

    # Display chat history
    st.subheader("Conversation History")

    # Move the CSS to a separate component using st.markdown
    st.markdown("""
        <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            margin-top: 10px;
        }
        .chat-bubble {
            max-width: 75%;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 15px;
            font-size: 16px;
            line-height: 1.5;
        }
        .user-bubble {
            background-color: #DCF8C6;
            align-self: flex-end;
            border: 1px solid #B9E9A8;
        }
        .ai-bubble {
            background-color: #ECECEC;
            align-self: flex-start;
            border: 1px solid #D4D4D4;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display each message separately
    if st.session_state["chat_history"]:
        for question, answer in st.session_state["chat_history"]:
            st.markdown(f'<div class="chat-bubble user-bubble" style="text-align: right">{question}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-bubble ai-bubble">{answer}</div>', unsafe_allow_html=True)
    else:
        st.info("Start a conversation by asking a question.")

if __name__ == "__main__":
    main()
