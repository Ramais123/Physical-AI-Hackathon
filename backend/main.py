from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from qdrant_client import QdrantClient
from fastapi.middleware.cors import CORSMiddleware

# 1. Setup & Config
load_dotenv()
app = FastAPI()

# --- CORS SETUP (Sabse Zaroori) ---
# Hum Vercel aur Localhost dono ko ijazat de rahe hain
# --- CORS SETUP (Bulletproof Method) ---
origins = [
    "http://localhost:3000",  # Laptop ke liye
    "https://physical-ai-hackathon.vercel.app",  # Main Domain
    # Neeche wali line wo URL hai jo aapke screenshot mein thi:
    "https://physical-ai-hackathon-x9cx-7swpbgacm.vercel.app" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Ab hum specific list de rahe hain
    allow_credentials=True, # Ab True rakhein, kyunke specific origin hai
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
api_key = os.getenv("GEMINI_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-flash-latest')

# Qdrant Client (Safe Mode)
try:
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    print("✅ Qdrant Connected")
except Exception as e:
    print(f"❌ Qdrant Error: {e}")

COLLECTION_NAME = "physical_ai_book"

# --- Request Models ---
class QueryRequest(BaseModel):
    question: str

class TranslateRequest(BaseModel):
    text: str

class PersonalizeRequest(BaseModel):
    text: str
    hardware: str

# --- Routes ---

@app.get("/")
def home():
    return {"message": "✅ Chatbot Brain is Online & CORS Fixed!"}

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    try:
        user_question = request.question
        # Embeddings
        embedding = genai.embed_content(
            model="models/text-embedding-004", content=user_question
        )['embedding']
        
        # Search (Safe Mode)
        try:
            search_result = client.search(
                collection_name=COLLECTION_NAME, query_vector=embedding, limit=3
            )
        except AttributeError:
            search_result = client.query_points(
                collection_name=COLLECTION_NAME, query=embedding, limit=3
            ).points

        context = ""
        if search_result:
            for hit in search_result:
                payload = hit.payload if hasattr(hit, 'payload') else hit.dict().get('payload', {})
                context += payload.get('text', '') + "\n\n"
        
        prompt = f"Answer based on context:\n{context}\nQuestion: {user_question}"
        response = model.generate_content(prompt)
        return {"answer": response.text}
    except Exception as e:
        return {"answer": f"Error: {str(e)}"}

@app.post("/translate")
def translate_endpoint(request: TranslateRequest):
    try:
        prompt = f"Translate to Urdu (Technical terms in English):\n{request.text}"
        response = model.generate_content(prompt)
        return {"translated_text": response.text}
    except Exception as e:
        return {"translated_text": "Translation Failed."}

@app.post("/personalize")
def personalize_endpoint(request: PersonalizeRequest):
    try:
        hw = request.hardware
        instruction = "Focus on Cloud/CPU simulation." if hw == 'cpu' else "Focus on NVIDIA Isaac Sim & RTX."
        prompt = f"Rewrite this textbook content. {instruction}\nOriginal:\n{request.text}"
        response = model.generate_content(prompt)
        return {"personalized_text": response.text}
    except Exception as e:
        return {"personalized_text": "Personalization Failed."}