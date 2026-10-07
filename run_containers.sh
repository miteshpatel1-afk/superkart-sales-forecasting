#!/usr/bin/env bash
# Build and run the SuperKart backend and frontend containers on a shared Docker network
set -e

# Network that lets the two containers talk to each other by name
docker network create superkart-net 2>/dev/null || true

# Remove old containers if the script is re-run
docker rm -f superkart-backend superkart-frontend 2>/dev/null || true

# Backend (Flask API on port 7860)
docker build -t superkart-backend ./backend_files
docker run -d --name superkart-backend --network superkart-net -p 7860:7860 superkart-backend

# Frontend (Streamlit UI on port 8501), pointed at the backend container
docker build -t superkart-frontend ./frontend_files
docker run -d --name superkart-frontend --network superkart-net -p 8501:8501 \
  -e BACKEND_URL=http://superkart-backend:7860 superkart-frontend

docker ps
echo "Backend:  port 7860  |  Frontend: port 8501"
