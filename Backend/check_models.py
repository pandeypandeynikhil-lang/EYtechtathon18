import os
from dotenv import load_dotenv
from google import genai

# 1. Load your API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env file.")
else:
    # 2. Connect to Google
    client = genai.Client(api_key=api_key)

    print("--- Models for Text/Chat (generateContent) ---")
    try:
        for m in client.models.list():
            if "generateContent" in m.supported_actions:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error: {e}")