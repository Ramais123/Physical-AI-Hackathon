import os
import glob
from dotenv import load_dotenv
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

# 1. Setup
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")

genai.configure(api_key=api_key)
client = QdrantClient(url=qdrant_url, api_key=qdrant_key)

COLLECTION_NAME = "physical_ai_book"

# 2. Database Collection Banana (Agar pehle se nahi hai)
try:
    client.get_collection(COLLECTION_NAME)
    print(f"✅ Collection '{COLLECTION_NAME}' already exists.")
except:
    print(f"⚙️ Creating collection '{COLLECTION_NAME}'...")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    )

# 3. Book Files Read Karna
# Hum dhoond rahe hain ke docs folder kahan hai
docs_path = os.path.join(os.path.dirname(__file__), "..", "physical-ai-book", "docs", "*.md")
files = glob.glob(docs_path)

print(f"📚 Found {len(files)} chapters to ingest.")

# 4. Processing & Uploading
point_id = 0

for file_path in files:
    file_name = os.path.basename(file_path)
    print(f"📖 Reading {file_name}...")
    
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Text ko chote tukron (chunks) mein todna taake AI samajh sake
    # Har 1000 characters ka ek chunk bana rahe hain
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    
    for i, chunk in enumerate(chunks):
        try:
            # Gemini se text ka "Vector" (Numbers) banwana
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=chunk
            )
            embedding = result['embedding']

            # Qdrant mein save karna
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={"filename": file_name, "text": chunk}
                    )
                ]
            )
            point_id += 1
            print(f"   Shape stored: Chunk {i+1}/{len(chunks)}")
            
        except Exception as e:
            print(f"❌ Error in chunk {i}: {e}")

print("🎉 Database Ingestion Complete! Chatbot is ready to learn.")