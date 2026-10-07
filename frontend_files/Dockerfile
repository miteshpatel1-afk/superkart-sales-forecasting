# Lightweight Python base image
FROM python:3.12-slim

# Working directory inside the container
WORKDIR /app

# Install Python dependencies first to take advantage of Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app
COPY . .

# Streamlit listens on port 8501
EXPOSE 8501

# Default backend address on the shared Docker network (can be overridden at docker run)
ENV BACKEND_URL=http://superkart-backend:7860

# CORS/XSRF disabled so file uploads work through the Codespaces port-forwarding proxy
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
