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

# --- 2. THE REGEX FIX (Jadoo) ---
# allow_origins=["*"] fail ho raha tha credentials ke sath.
# allow_origin_regex=".*" ka matlab: "Har naam allow hai"
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",  # <--- YEH HAI SOLUTION (Regex matches everything)
    allow_credentials=True,   # Ab credentials 100% chalenge
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. ROUTES ---

@app.get("/")
def home():
    return {"message": "✅ Brain is Online (Regex Mode)"}

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
        
        # Safe Check
        if not model: return {"personalized_text": "Error: API Key Missing"}
        
        response = model.generate_content(prompt)
        return {"personalized_text": response.text}
    except Exception as e:
        return JSONResponse(status_code=200, content={"personalized_text": f"Error: {str(e)}"})

@app.post("/translate")
def translate(request: BaseModel):
    try:
        data = request.dict() if hasattr(request, 'dict') else {}
        text = getattr(request, 'text', data.get('text', ''))
        
        if not model: return {"translated_text": "Error: API Key Missing"}

        prompt = f"Translate to Urdu:\n{text}"
        response = model.generate_content(prompt)
        return {"translated_text": response.text}
    except Exception as e:
        return JSONResponse(status_code=200, content={"translated_text": "Translation Failed"})