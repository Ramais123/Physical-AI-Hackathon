from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 1. Load Keys
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Configure AI (Error Handling ke saath)
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY nahi mili!")
else:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# --- 3. FINAL CORS FIX (Sabse Aasaan Wala) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Sabko allow karein
    allow_credentials=False, # Credentials band karein (Security rule)
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Models ---
class PersonalizeRequest(BaseModel):
    text: str
    hardware: str

class TranslateRequest(BaseModel):
    text: str

# --- Routes ---
@app.get("/")
def home():
    return {"message": "✅ Brain is Online (Safe Mode)"}

@app.post("/personalize")
async def personalize_endpoint(request: PersonalizeRequest):
    print(f"📩 Request aayi: {request.hardware}") # Log mein dikhega
    try:
        if not api_key:
            return {"personalized_text": "Error: Server par API Key missing hai."}

        instruction = "Focus on Cloud/CPU." if request.hardware == 'cpu' else "Focus on NVIDIA RTX/Isaac Sim."
        prompt = f"Rewrite this textbook content. {instruction}\nOriginal:\n{request.text}"
        
        response = model.generate_content(prompt)
        print("✅ AI ne jawab de diya")
        return {"personalized_text": response.text}

    except Exception as e:
        print(f"❌ ERROR AYA: {str(e)}") # Ye Render Logs mein aayega
        # Error aane par bhi JSON bhejen taake CORS error na aye
        return JSONResponse(
            status_code=200, 
            content={"personalized_text": f"AI Error: {str(e)}"}
        )

@app.post("/translate")
async def translate_endpoint(request: TranslateRequest):
    try:
        prompt = f"Translate to Urdu:\n{request.text}"
        response = model.generate_content(prompt)
        return {"translated_text": response.text}
    except Exception as e:
        print(f"❌ Translate Error: {str(e)}")
        return JSONResponse(status_code=200, content={"translated_text": "Translation Failed."})

@app.post("/chat")
async def chat_dummy(request: dict):
    # Chatbot fallback agar Qdrant na ho
    return {"answer": "Chatbot is working!"}