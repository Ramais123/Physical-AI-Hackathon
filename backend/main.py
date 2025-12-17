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

# CORS: Frontend ko allow karna
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys Load Karna
api_key = os.getenv("GEMINI_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")

# Gemini Setup
genai.configure(api_key=api_key)
# Model: 'gemini-flash-latest' use kar rahe hain.
# Agar quota error aye toh 'gemini-pro' kar dein.
model = genai.GenerativeModel('gemini-flash-latest')

# Qdrant Database Setup
client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
COLLECTION_NAME = "physical_ai_book"

class QueryRequest(BaseModel):
    question: str

class TranslateRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "✅ Chatbot Brain is Online!"}

@app.post("/chat")
def chat_endpoint(request: QueryRequest):
    user_question = request.question
    print(f"📩 Sawal aaya: {user_question}")

    try:
        # Step 1: Sawal ka Vector (Embedding) Banana
        embedding_result = genai.embed_content(
            model="models/text-embedding-004",
            content=user_question
        )
        embedding = embedding_result['embedding']
        
        # Step 2: Database Search (Safe Mode)
        # Hum check karenge ke konsa function available hai
        search_result = []
        
        try:
            # Option A: Standard Search (New Versions)
            search_result = client.search(
                collection_name=COLLECTION_NAME,
                query_vector=embedding,
                limit=3
            )
        except AttributeError:
            # Option B: Fallback Search (Older Versions)
            print("⚠️ Standard search failed, trying fallback...")
            search_result = client.query_points(
                collection_name=COLLECTION_NAME,
                query=embedding,
                limit=3
            ).points

        # Agar Database mein kuch na mile
        if not search_result:
            return {"answer": "Mujhe iska jawab kitab mein nahi mila. Shayad ingestion abhi tak nahi hui."}

        # Step 3: Context Jama Karna
        context = ""
        for hit in search_result:
            # Payload safe tareeqe se nikalna
            if hasattr(hit, 'payload'):
                text = hit.payload.get('text', '')
            else:
                # Kabhi kabhi payload dictionary ki tarah access hota hai
                text = hit.payload['text']
            
            context += text + "\n\n"

        # Step 4: Gemini se Jawab Likhwana
        prompt = f"""
        You are an AI Tutor for the 'Physical AI & Humanoid Robotics' course.
        Answer the student's question based ONLY on the provided Context below.
        
        Context from Book:
        {context}
        
        Student Question: {user_question}
        
        Answer (Keep it concise and helpful):
        """
        
        response = model.generate_content(prompt)
        return {"answer": response.text}

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"answer": f"System Error: {str(e)}. Terminal check karein details ke liye."}
    
@app.post("/translate")
def translate_endpoint(request: TranslateRequest):
    text_to_translate = request.text
    print(f"🔄 Translating text length: {len(text_to_translate)}")

    try:
        # Prompt: Technical Urdu translation
        prompt = f"""
        Translate the following technical Robotics/AI text into Urdu.
        Rules:
        1. Keep technical terms (ROS 2, Python, Nodes, LiDAR, Gazebo) in ENGLISH.
        2. Translate the explanation into clear, easy-to-understand Urdu.
        3. Do not shorten the content, translate everything.
        
        Text to Translate:
        {text_to_translate}
        """
        
        response = model.generate_content(prompt)
        return {"translated_text": response.text}

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"translated_text": "Translation Failed. Server Check karein."}

class PersonalizeRequest(BaseModel):
    text: str
    hardware: str  # 'gpu' ya 'cpu'

@app.post("/personalize")
def personalize_endpoint(request: PersonalizeRequest):
    text_content = request.text
    user_hardware = request.hardware
    print(f"⚙️ Personalizing for: {user_hardware}")

    try:
        # Prompt: Content ko User ke liye adjust karna
        system_instruction = ""
        if user_hardware == "cpu":
            system_instruction = """
            The user ONLY has a CPU (No NVIDIA GPU). 
            Rewrite the technical content to focus on 'Cloud-Based Simulation (AWS/Google Colab)' 
            and 'Low-Poly Proxies' instead of heavy local rendering.
            Replace 'Isaac Sim' instructions with 'Gazebo (CPU Mode)' or cloud alternatives.
            Keep it encouraging but realistic.
            """
        else:
            system_instruction = """
            The user has a High-End NVIDIA RTX GPU.
            Rewrite the technical content to focus on 'Photorealistic Rendering', 'Ray Tracing', 
            and 'Isaac Sim' full capabilities. Encourage heavy physics simulations.
            """

        prompt = f"""
        Act as a Textbook Editor. 
        {system_instruction}
        
        Original Text:
        {text_content}
        
        Output the modified text in clear Markdown format.
        """
        
        response = model.generate_content(prompt)
        return {"personalized_text": response.text}

    except Exception as e:
        return {"personalized_text": "Personalization Failed. Server check karein."}