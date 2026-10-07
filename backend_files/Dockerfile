# Lightweight Python base image (Python 3.12 matches the training environment)
FROM python:3.12-slim

# libgomp is required by XGBoost for multi-threaded prediction
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*

# Working directory inside the container
WORKDIR /app

# Install Python dependencies first to take advantage of Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API code and the serialized model
COPY . .

# The API listens on port 7860
EXPOSE 7860

# Serve the Flask app with gunicorn (production-grade WSGI server)
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "app:superkart_api"]
