from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import google.generativeai as genai
from fastapi.responses import JSONResponse

app = FastAPI()

# --- 1. SETUP API KEY ---
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. CORS (Specific Origins Only) ---
# Hum '*' nahi use karenge. Hum exact link denge.
origins = [
    "http://localhost:3000",                                      # Laptop Testing
    "https://physical-ai-hackathon.vercel.app",                   # Main Website
    "https://physical-ai-hackathon-x9cx-7swpbgacm.vercel.app"     # 👈 AAPKA VERCEL PREVIEW LINK (Jo error de raha tha)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # Sirf in 3 links ko ijazat hai
    allow_credentials=True,   # Ab hum TRUE rakh sakte hain kyunke specific links hain
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. ROUTES ---
@app.get("/")
def home():
    return {"message": "✅ Brain is Online (Specific Access Mode)"}

@app.head("/")
def health_check():
    return {"status": "ok"}

class PersonalizeRequest(BaseModel):
    text: str
    hardware: str

@app.post("/personalize")
def personalize(request: PersonalizeRequest):
    try:
        instruction = "Focus on Cloud/CPU simulation." if request.hardware == 'cpu' else "Focus on NVIDIA Isaac Sim & RTX."
        prompt = f"Rewrite this content. {instruction}\nOriginal:\n{request.text}"
        
        response = model.generate_content(prompt)
        return {"personalized_text": response.text}
    except Exception as e:
        return JSONResponse(status_code=200, content={"personalized_text": f"Error: {str(e)}"})

@app.post("/translate")
def translate(request: BaseModel):
    try:
        # Flexible handling for text
        data = request.dict() if hasattr(request, 'dict') else {}
        text = getattr(request, 'text', data.get('text', ''))
        
        prompt = f"Translate to Urdu:\n{text}"
        response = model.generate_content(prompt)
        return {"translated_text": response.text}
    except Exception as e:
        return JSONResponse(status_code=200, content={"translated_text": "Translation Failed"})