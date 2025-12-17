import os
from dotenv import load_dotenv
import google.generativeai as genai
from qdrant_client import QdrantClient

# 1. Keys Load karna
load_dotenv()
print("----- 🔍 SYSTEM CHECK START -----")

# 2. Gemini Check
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    print("✅ Gemini Key Found!")
    try:
        genai.configure(api_key=gemini_key)
        
        # CHANGE: 'gemini-flash-latest' use kar rahe hain jo aapki list mein tha
        model = genai.GenerativeModel('gemini-flash-latest')
        
        response = model.generate_content("Say 'Hello Boss' if you can hear me.")
        print(f"🤖 Gemini Says: {response.text.strip()}")
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
else:
    print("❌ Gemini Key NOT Found. Check .env file.")

# 3. Qdrant Database Check
qdrant_url = os.getenv("QDRANT_URL")
qdrant_key = os.getenv("QDRANT_API_KEY")

if qdrant_url and qdrant_key:
    print("✅ Qdrant Keys Found!")
    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
        collections = client.get_collections()
        print("🗄️ Database Connected Successfully!")
    except Exception as e:
        print(f"❌ Qdrant Connection Failed: {e}")
else:
    print("❌ Qdrant Keys NOT Found. Check .env file.")

print("----- 🏁 CHECK COMPLETE -----")