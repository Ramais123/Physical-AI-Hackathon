from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import google.generativeai as genai
from qdrant_client import QdrantClient
from fastapi.responses import JSONResponse

# --------------------------------------------------
# 1. APP + ENV SETUP
# --------------------------------------------------
load_dotenv()
app = FastAPI(title="Physical AI Book RAG Backend")

# CORS (Vercel / Browser Safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # prod mein frontend URL laga do
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# 2. ENV VARIABLES
# --------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = "physical_ai_book"

# --------------------------------------------------
# 3. GEMINI SETUP
# --------------------------------------------------
# GEMINI SETUP
model = None
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")


# --------------------------------------------------
# 4. QDRANT SETUP
# --------------------------------------------------
client = None
if QDRANT_URL and QDRANT_API_KEY:
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    except Exception as e:
        print("❌ Qdrant connection failed:", e)

# --------------------------------------------------
# 5. HEALTH CHECK
# --------------------------------------------------
@app.get("/")
def health():
    return {
        "status": "Backend Live ✅",
        "gemini": model.model_name if model else "Not Configured",
        "qdrant": "Connected" if client else "Not Connected"
    }

# ------------------------ PERSONALIZE ENDPOINT ------------------------
@app.post("/personalize")
async def personalize(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "")
        hardware = data.get("hardware", "cpu")

        # ignore frontend model param completely
        focus = "Focus on cloud and CPU simulation." if hardware == "cpu" else "Focus on NVIDIA Isaac Sim and RTX GPUs."
        prompt = f"Rewrite this textbook content for a student.\n{focus}\n\nContent:\n{text}"

        response = model.generate_content(prompt)
        return {"personalized_text": response.text}

    except Exception as e:
        return {"personalized_text": f"Error: {str(e)}"}


# ------------------------ CHAT ENDPOINT ------------------------
@app.post("/chat")
async def chat(request: Request):
    try:
        if not model or not client:
            return JSONResponse(
                status_code=500,
                content={"answer": "AI services not configured"}
            )

        data = await request.json()
        question = data.get("question")
        if not question:
            return {"answer": "Question is required"}

        # ---- Embedding (ONE MODEL ONLY - safe) ----
        emb_response = genai.embed_content(
            model="models/text-embedding-004",
            content=question
        )
        query_vector = emb_response["embedding"]

        # ---- Qdrant Search ----
        search_results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=4
        )

        context = "\n".join([hit.payload.get("text", "") for hit in search_results])

        prompt = f"""
You are a textbook assistant.
Answer ONLY using the context below.
If the answer is not present, say: "Not found in the book."

Context:
{context}

Question:
{question}
"""
        response = model.generate_content(prompt)
        return {"answer": response.text}

    except Exception as e:
        return {"answer": f"Error: {str(e)}"}

# --------------------------------------------------
# 7. TRANSLATION
# --------------------------------------------------
@app.post("/translate")
async def translate(request: Request):
    data = await request.json()
    text = data.get("text", "")

    prompt = f"""
Translate the following technical content to Urdu.
Keep English technical terms unchanged.

{text}
"""
    response = model.generate_content(prompt)
    return {"translated_text": response.text}

# --------------------------------------------------
# 8. PERSONALIZATION
# --------------------------------------------------
@app.post("/personalize")
async def personalize(request: Request):
    data = await request.json()
    text = data.get("text", "")
    hardware = data.get("hardware", "cpu")

    focus = (
        "Focus on cloud and CPU simulation."
        if hardware == "cpu"
        else "Focus on NVIDIA Isaac Sim and RTX GPUs."
    )

    prompt = f"""
Rewrite this textbook content for a student.
{focus}

Content:
{text}
"""
    response = model.generate_content(prompt)
    return {"personalized_text": response.text}

# --------------------------------------------------
# 9. PREFLIGHT (CORS SAFETY)
# --------------------------------------------------
@app.options("/{path:path}")
async def options_handler():
    return Response(status_code=200)
