# Use the official Python image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose port 8080
EXPOSE 8080

# Command to run the Streamlit app
CMD ["streamlit", "run", "app/chat_with_documents.py", "--server.port=8080", "--server.address=0.0.0.0"]
