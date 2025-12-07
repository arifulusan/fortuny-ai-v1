from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

app = FastAPI()

class FortuneRequest(BaseModel):
    mood: str
    streak: int

@app.post("/api/fortune")
async def generate_fortune(request: FortuneRequest):
    try:
        prompt = f"""
        You are a mystic fortune teller from a pixelated cyberpunk fantasy world.
        The user's mood is: {request.mood}
        Their streak is: {request.streak} days.

        Generate a unique fortune card for them.
        Return ONLY a raw JSON object (no markdown formatting) with these exact keys:
        - card_name: A short, cool title (e.g., "THE GLITCH", "NEON DRAGON", "VOID WALKER").
        - fortune_text: A 1-2 sentence fortune, mysterious but relevant to the mood. Write in Turkish.
        - art_type: One of [fire, ice, skull, battery, rune, sword, potion, chest, coin, heart, glitch]. Choose the one that best fits the fortune.
        - color_theme: One of [red, blue, yellow, purple, green, gray].

        JSON:
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up potential markdown code blocks if the model adds them
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text)
    except Exception as e:
        print(f"Error generating fortune: {e}")
        # Fallback response in case of error
        return {
            "card_name": "THE VOID",
            "fortune_text": "Evrenin sinyalleri karışık. Daha sonra tekrar dene.",
            "art_type": "glitch",
            "color_theme": "gray"
        }

class TarotRequest(BaseModel):
    card_name: str

@app.post("/api/tarot-fortune")
async def generate_tarot_fortune(request: TarotRequest):
    try:
        prompt = f"""
        You are a mystic tarot reader.
        The card drawn is: {request.card_name}
        
        Generate a very short fortune/interpretation for this card.
        Return ONLY a raw JSON object (no markdown formatting) with these exact keys:
        - fortune_text: A single short sentence (max 10 words) interpretation of the card. Write in Turkish.
        
        JSON:
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text)
    except Exception as e:
        print(f"Error generating tarot fortune: {e}")
        return {
            "fortune_text": "Kartların enerjisi şu an kapalı."
        }

# Mount static files - this must be last to not override API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)