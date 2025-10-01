import os
import re
import json
import requests
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from huggingface_hub import InferenceClient

# ---------------- CONFIG ----------------
HF_MODEL = "CohereLabs/command-a-translate-08-2025"  # Cohere LLM
HF_PROVIDER = "cohere"
HF_API_KEY = os.getenv("HF_API_KEY")  
print(HF_API_KEY)
MAX_RESULTS = 5

# ---------------- FASTAPI ----------------
app = FastAPI(title="Restaurant Chatbot")

client = InferenceClient(provider=HF_PROVIDER, api_key=HF_API_KEY)

# ---------------- FALLBACK DATA ----------------
fallback_data = [
    {"name": "Green Veggie", "cuisine": "Vegetarian", "location": "Indiranagar", "menu": "Paneer Tikka, Dal Fry, Roti"},
    {"name": "Pizza Palace", "cuisine": "Italian", "location": "Koramangala", "menu": "Margherita, Farmhouse, Pepperoni"},
    {"name": "Sushi Zen", "cuisine": "Japanese", "location": "MG Road", "menu": "Sushi Roll, Miso Soup, Tempura"},
    {"name": "Burger Hub", "cuisine": "American", "location": "Whitefield", "menu": "Cheeseburger, Fries, Coke"},
    {"name": "Tandoori Tales", "cuisine": "Indian", "location": "Jayanagar", "menu": "Tandoori Chicken, Naan, Paneer Butter Masala"},
]

# ---------------- UTILITIES ----------------
def parse_intent(query: str) -> str:
    q = query.lower()
    if "menu" in q or "dish" in q:
        return "menu"
    if "open" in q or "hours" in q:
        return "hours"
    return "search"

def extract_location(query: str) -> Optional[str]:
    m = re.search(r"in ([A-Za-z ]+)", query)
    return m.group(1).strip() if m else None

def extract_cuisine(query: str) -> Optional[str]:
    cuisines = ["vegetarian", "italian", "japanese", "american", "indian", "sushi", "pizza", "burger"]
    for c in cuisines:
        if c in query.lower():
            return c
    return None

# ---------------- RESTAURANT SEARCH ----------------
def search_restaurants(query, location=None, cuisine=None, limit=MAX_RESULTS):
    search_terms = "restaurant"
    if cuisine:
        search_terms += f" {cuisine}"
    if location:
        search_terms += f" {location}"

    url = f"https://nominatim.openstreetmap.org/search.php?q={search_terms}&format=jsonv2&limit={limit}"
    try:
        headers = {
        "User-Agent": "RestaurantBot/1.0 (your_email@example.com)"
        }

        resp = requests.get(url, headers=headers, timeout=10)

        print("Nominatim URL:", url)
        print("Response status code:", resp.status_code)
        print("Response JSON:", resp.json())

        data = resp.json()
        results = []
        for r in data:
            results.append({
                "name": r.get("display_name", "Unknown"),
                "location": r.get("address", {}).get("city", location if location else "Unknown"),
                "lat": r.get("lat"),
                "lon": r.get("lon")
            })
        if results:
            return results
    except Exception as e:
        print("Nominatim API failed:", e)

    # fallback
    filtered = fallback_data
    if location:
        filtered = [r for r in filtered if location.lower() in r["location"].lower()]
    if cuisine:
        filtered = [r for r in filtered if cuisine.lower() in r["cuisine"].lower()]
    return filtered[:limit]

# ---------------- PROMPT ----------------
def build_prompt(intent, query, restaurants):
    system_prompt = """
You are DineBot, a helpful restaurant assistant.
Use ONLY the provided restaurant list.
Always return JSON:
{"restaurants": [...], "explanation": "..."}
"""
    few_shots = [
        {
            "user": "Find vegetarian restaurants in Indiranagar",
            "assistant": '{"restaurants": ["Green Veggie"], "explanation": "Green Veggie is a highly rated vegetarian restaurant in Indiranagar."}'
        },
        {
            "user": "Suggest Japanese food near MG Road",
            "assistant": '{"restaurants": ["Sushi Zen"], "explanation": "Sushi Zen is a popular Japanese restaurant near MG Road with authentic sushi."}'
        }
    ]
    context = "\n".join([f"- {r['name']}, {r.get('location','')}" for r in restaurants]) if restaurants else "No restaurants found."
    prompt = system_prompt
    for shot in few_shots:
        prompt += f"\nUser: {shot['user']}\nAssistant: {shot['assistant']}"
    prompt += f"\nContext:\n{context}\nUser: {query}\nAssistant:"
    return prompt

# ---------------- LLM CALL ----------------
def call_llm(prompt: str):
    if not HF_API_KEY:
        return json.dumps({"restaurants": [], "explanation": "HF_API_KEY not set. Cannot call LLM."})
    try:
        completion = client.chat.completions.create(
            model=HF_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        return json.dumps({"restaurants": [], "explanation": f"LLM Error: {str(e)}"})

# ---------------- API ----------------
class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat(request: ChatRequest):
    query = request.query
    intent = parse_intent(query)
    location = extract_location(query)
    cuisine = extract_cuisine(query)
    restaurants = search_restaurants(query, location, cuisine)
    prompt = build_prompt(intent, query, restaurants)
    llm_resp = call_llm(prompt)
    try:
        parsed = json.loads(llm_resp)
    except:
        parsed = {"restaurants": [r["name"] for r in restaurants], "explanation": llm_resp}
    return {"parsed": parsed, "raw": llm_resp}

# ---------------- RUN ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("restaurant_api:app", host="127.0.0.1", port=8000, reload=True)
