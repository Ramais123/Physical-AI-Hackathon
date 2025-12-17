from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import os
import google.generativeai as genai
from fastapi.responses import JSONResponse

app = FastAPI()

# --- 1. SETUP API ---
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. THE NUCLEAR CORS FIX (Mirror Method) ---
# Yeh middleware har request ke headers ko modify karega
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    # Incoming Origin ko pakdo (e.g. https://vercel-app...)
    origin = request.headers.get("origin")
    
    # Agar ye Preflight (OPTIONS) check hai, toh foran HAAN bol do
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        # Asal request ko process karein
        try:
            response = await call_next(request)
        except Exception as e:
            response = JSONResponse(status_code=500, content={"error": str(e)})

    # Ab Jawab mein headers chipka do
    # Jo Origin aya tha, wapis wahi bhej do (Taake browser khush rahe)
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
        
    response.headers["Access-Control-Allow-Credentials"] = "true" # Ab Credentials bhi allowed hain
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

# --- 3. ROUTES ---
@app.get("/")
def home():
    return {"message": "✅ Brain is Online (Mirror Mode)"}

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
        # Flexible Data Handling
        data = request.dict() if hasattr(request, 'dict') else {}
        text = getattr(request, 'text', data.get('text', ''))
        
        prompt = f"Translate to Urdu:\n{text}"
        response = model.generate_content(prompt)
        return {"translated_text": response.text}
    except Exception as e:
        return JSONResponse(status_code=200, content={"translated_text": "Translation Failed"})