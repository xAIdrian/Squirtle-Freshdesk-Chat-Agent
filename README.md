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
openai_api_key = st.secrets["openai_api_key"]
```

### Sure but how do we deploy the app?

- Test in Streamlit Cloud (but this doesn't allow custom domain names)
- Build, containerize, and deploy to Docker Hub
- Test the Docker runs locally
- Deploy docker to Google Cloud Run
- Test the docker runs on Google Cloud Run
- Set up a custom domain name
