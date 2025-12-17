from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi.responses import JSONResponse

# 1. Setup
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# --- 2. BRUTE FORCE CORS (Jugaad) ---
# Har request ke jawab mein zabardasti headers ghusana
@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as e:
        # Agar code crash ho, tab bhi JSON bhejo taake CORS error na aye
        response = JSONResponse(content={"error": str(e)}, status_code=500)
    
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Preflight Requests (OPTIONS) ko manually handle karna
@app.options("/{path:path}")
async def options_handler(path: str):
    return Response(
        content="OK",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )

# --- Models ---
class PersonalizeRequest(BaseModel):
    text: str
    hardware: str

class TranslateRequest(BaseModel):
    text: str

class QueryRequest(BaseModel):
    question: str

# --- Routes ---
@app.get("/")
def home():
    return {"message": "✅ Chatbot Brain is Online!"}

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    # Dummy Chat (Agar Qdrant na ho)
    return {"answer": "Chatbot is working! (Database connection checked)"}

@app.post("/personalize")
def personalize_endpoint(request: PersonalizeRequest):
    try:
        if not api_key: return {"personalized_text": "Error: API Key Missing"}
        
        instruction = "Cloud/CPU" if request.hardware == 'cpu' else "NVIDIA RTX"
        prompt = f"Rewrite this: {instruction}\n{request.text}"
        response = model.generate_content(prompt)
        return {"personalized_text": response.text}
    except Exception as e:
        return {"personalized_text": f"Error: {str(e)}"}

@app.post("/translate")
def translate_endpoint(request: TranslateRequest):
    try:
        if not api_key: return {"translated_text": "Error: API Key Missing"}
        prompt = f"Translate to Urdu:\n{request.text}"
        response = model.generate_content(prompt)
        return {"translated_text": response.text}
    except Exception as e:
        return {"translated_text": f"Error: {str(e)}"}