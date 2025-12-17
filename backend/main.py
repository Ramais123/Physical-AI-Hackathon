from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import google.generativeai as genai
from fastapi.responses import JSONResponse

app = FastAPI()

# --- 1. CORS FIX (Sabse Zaroori) ---
# Rule: Agar Origins=["*"] hai, toh Credentials=False hona chahiye.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Duniya ki har website allow
    allow_credentials=False,  # Isay FALSE rakhna zaroori hai '*' ke sath
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. SETUP ---
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. ROUTES ---

@app.get("/")
def home():
    return {"message": "✅ Brain is Online & CORS Fixed!"}

# Render Health Check (Jo logs mein 405 de raha tha, usay chup karane ke liye)
@app.head("/")
def health_check():
    return {"status": "ok"}

class PersonalizeRequest(BaseModel):
    text: str
    hardware: str

@app.post("/personalize")
def personalize(request: PersonalizeRequest):
    try:
        # Instruction logic
        instruction = "Focus on Cloud/CPU simulation." if request.hardware == 'cpu' else "Focus on NVIDIA Isaac Sim & RTX."
        prompt = f"Rewrite this textbook content. {instruction}\nOriginal:\n{request.text}"
        
        response = model.generate_content(prompt)
        return {"personalized_text": response.text}
    except Exception as e:
        # Error ko bhi 200 OK banakar bhejo taake CORS na roke
        return JSONResponse(status_code=200, content={"personalized_text": f"Error: {str(e)}"})

@app.post("/translate")
def translate(request: BaseModel): # Generic model
    try:
        # Request body se text nikalna (Flexible handling)
        data = request.dict()
        text_content = data.get('text', '')
        
        prompt = f"Translate to Urdu:\n{text_content}"
        response = model.generate_content(prompt)
        return {"translated_text": response.text}
    except Exception as e:
        return JSONResponse(status_code=200, content={"translated_text": "Translation Failed"})