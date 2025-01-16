python3 -m pip install openai langchain streamlit pandas

mkdir .streamlit
touch .streamlit/secrets.toml
openai_api_key = "sk-your-actual-api-key-here"

For Production/Streamlit Cloud:
Go to your app dashboard on Streamlit Cloud
Navigate to App Settings > Secrets
Add your secret in the same format:
```
openai_api_key = "sk-your-actual-api-key-here"
```
You can then access the secret in your code using:
```
openai.api_key = st.secrets["openai_api_key"]
```
