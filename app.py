import streamlit as st
import json
from ottobot import get_ottobot_with_vectore_store, load_thread_messages, run_new_thread_submit_message

thread_id = None

def main():
    st.title("Ask Mark Ottobre 💪")
    # Initialize chat history in session state if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Initialize simplest ottobot
    ottobot = get_ottobot_with_vectore_store("ottobotV2", [
        "docs/CALCULATOR A.M. Nutrition & Lifestyle Protocol Data Sources.pdf",
        "docs/MACROS A.M. Nutrition & Lifestyle Protocol Data Sources.pdf",
        "docs/MACROS Mark Ottobre Master File Data Sources.pdf",
        "docs/Mark Ottobre Master File Data Sources.pdf",
        "docs/Mark Ottobre Master File.pdf",
        "docs/MEAL PLANS A.M. Nutrition & Lifestyle Protocol Data Sources.pdf",
        "docs/OVERVIEW A.M. Nutrition & Lifestyle Protocol Data Sources.pdf",
        "docs/PROGRAM Mark Ottobre Master File Data Sources.pdf",
        "docs/SYSTEM Mark Ottobre Master File Data Sources.pdf",
        "docs/TIMELINE A.M. Nutrition & Lifestyle Protocol Data Sources.pdf",
        "docs/TIMELINE Mark Ottobre Master File Data Sources.pdf",
        "docs/The Enterprise Diet.pdf",
        "docs/ENTERPRISE FITNESS - USER MANUAL.pdf",
    ])

    # Chat UI
    st.subheader("All the information you need to take your training to the next level")
    user_question = st.text_input("Ask a question:", "")

    # Sidebar for Thread ID
    st.sidebar.header("Manage Threads")
    st.sidebar.caption("Create a new thread or load an existing thread")

    with st.sidebar:
        thread_id = st.text_input("Thread ID:", key="thread_id")
        if st.button("Load Thread"):
            messages = load_thread_messages(thread_id)

            if messages is None:
                st.sidebar.error("Thread not found. Please start a new conversation.")
            else:
                for message in messages:
                    st.session_state["chat_history"].append((message.content[0].text.value, ""))

    if st.button("Send"):
        if user_question.strip():
            with st.spinner("Generating response..."):
                response = run_new_thread_submit_message(ottobot.id, user_question)
                for chunk in response:
                    if hasattr(chunk, 'event') and chunk.event == 'thread.message.delta':
                        try:
                            print("Object variables:", vars(chunk), end="\n\n")
                        except:
                            print("vars() not available for this object")
                        
                        # Extract the new text
                        if hasattr(chunk, 'data') and hasattr(chunk.data, 'delta'):
                            new_text = chunk.data.delta.content[0].text.value
                            full_response += new_text
                
                # Once streaming is complete, add to chat history
                if full_response:
                    st.session_state["chat_history"].append((user_question, full_response))

                # # If it's bytes, decode it to string and parse JSON
                # if isinstance(response_data, bytes):
                #     import json
                #     response_json = json.loads(response_data.decode('utf-8'))
                # else:
                #     response_json = response_data

                # # Now you can access the data
                # text = response_json.delta.content[0].text.value
                # print(text)
                # st.session_state["chat_history"].append((user_question, text))

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
