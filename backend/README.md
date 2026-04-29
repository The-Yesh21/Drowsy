# Drowsiness Detector Backend

This is the FastAPI backend for the drowsy driver detection system. It handles driver authentication, session tracking, real-time event ingestion via WebSockets, and AI safety analytics using Google Gemini Flash.

## Setup

1. Create a Python 3.12 environment (or similar)
2. `pip install -r requirements.txt`
3. Edit `.env` with your real MongoDB Atlas connection string and Gemini API Key.
4. Run server: `uvicorn main:app --reload`
