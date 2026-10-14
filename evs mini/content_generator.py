"""
content_generator.py
====================
This file handles all AI content generation using Ollama (runs 100% locally).

How it works (for beginners):
- Ollama runs a local AI model on YOUR computer (no internet or API key needed!)
- We send the user's topic and chosen language to the local model
- We ask it to return a headline, message, tips, and slogan as JSON
- We parse the JSON and return it as a Python dictionary
- If anything goes wrong, we return an error message
"""

import os
import requests   # For sending HTTP requests
import json       # For parsing JSON responses
import re         # For text cleanup
from dotenv import load_dotenv

load_dotenv()

# ── Ollama settings ────────────────────────────────────────────────────────────
OLLAMA_LOCAL_URL = "http://localhost:11434/api/generate"  # Local Ollama address
OLLAMA_CLOUD_URL = "https://ollama.com/api/chat"           # Ollama Cloud address
OLLAMA_MODEL     = "llama3.2"                             # Local model
OLLAMA_CLOUD_MODEL = "gemma4:31b"                         # Cloud model
OLLAMA_API_KEY   = os.getenv("OLLAMA_API_KEY", "")


# Curated offline templates for standard topics in case services are unreachable
OFFLINE_TEMPLATES = {
    "save trees": {
        "headline": "Plant a Seed, Grow a Future, Save Our Trees",
        "message": "Trees produce the oxygen we breathe, clean our air, and shelter wildlife. Every tree saved protects our future from climate catastrophe.",
        "tips": [
            "Plant native saplings in your community and care for them",
            "Switch to digital documents and recycle paper products",
            "Support local forestry and tree protection drives"
        ],
        "slogan": "Root for the Earth: Save Trees Today!"
    },
    "save water": {
        "headline": "Every Drop Counts: Conserve Water Every Day",
        "message": "Clean freshwater is life's most precious resource, yet billions face water scarcity. Mindful usage at home can save thousands of liters annually.",
        "tips": [
            "Fix leaking faucets and use aerators to reduce flow",
            "Turn off the tap while brushing or washing dishes",
            "Collect rainwater for gardening and household cleaning"
        ],
        "slogan": "Conserve Water, Secure Tomorrow's Life!"
    },
    "reduce plastic pollution": {
        "headline": "Break Free from Plastic: Protect Our Living Planet",
        "message": "Single-use plastics choke our oceans, harm animals, and break down into microplastics. Choosing sustainable alternatives creates a cleaner world.",
        "tips": [
            "Always carry a reusable cloth bag and steel water bottle",
            "Say no to single-use plastic straws, cutlery, and wraps",
            "Participate in local park and beach cleanup drives"
        ],
        "slogan": "Refuse Single-Use: Beat Plastic Pollution!"
    },
    "climate change": {
        "headline": "Act on Climate Now: The Future Depends on Us",
        "message": "Rising temperatures and extreme weather threaten ecosystems worldwide. Individual action combined with community leadership drives real change.",
        "tips": [
            "Use public transport, carpool, or cycle for daily commutes",
            "Unplug unused electronics and adopt energy-efficient appliances",
            "Eat more plant-based meals to lower your carbon footprint"
        ],
        "slogan": "Change Your Habits, Not the Climate!"
    }
}


def _parse_and_validate(raw_text: str):
    """Clean and parse JSON from model output."""
    cleaned = re.sub(r"```(?:json)?", "", raw_text).replace("```", "").strip()
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not json_match:
        return None, "AI did not return valid JSON."
    
    content = json.loads(json_match.group())
    required_keys = ["headline", "message", "tips", "slogan"]
    for key in required_keys:
        if key not in content:
            return None, f"AI response missing '{key}'."
    
    if not isinstance(content["tips"], list) or len(content["tips"]) < 3:
        return None, "AI response must contain at least 3 tips."
    content["tips"] = content["tips"][:3]
    return content, None


def generate_awareness_content(topic: str, language: str = "English", api_key: str = None):
    """
    Generate environmental awareness content using local Ollama model,
    falling back to Ollama Cloud API, or curated templates.
    """
    prompt = f"""You are an expert environmental awareness educator. Generate content for a poster.

Topic: "{topic}"
Language: {language}

Write ALL content in {language} only. Use simple words everyone can understand.
Be positive, inspiring, and motivating. Keep it concise.

Return ONLY a valid JSON object like this (no explanation, no extra text):

{{
  "headline": "A strong headline about {topic} (max 12 words)",
  "message": "A meaningful message explaining why {topic} matters (2-3 sentences)",
  "tips": [
    "First practical tip anyone can do",
    "Second practical tip about {topic}",
    "Third practical tip about {topic}"
  ],
  "slogan": "A short catchy slogan about {topic} (max 10 words)"
}}

IMPORTANT: Return ONLY the JSON. No markdown, no explanation, no extra text."""

    # ── Attempt 1: Local Ollama (llama3.2) ──
    try:
        response = requests.post(
            OLLAMA_LOCAL_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500
                }
            },
            timeout=30
        )
        if response.status_code == 200:
            raw_text = response.json().get("response", "").strip()
            content, err = _parse_and_validate(raw_text)
            if content:
                return content, None
    except Exception as e:
        # Local Ollama failed or timed out, try cloud fallback
        pass

    # ── Attempt 2: Ollama Cloud API ──
    effective_key = api_key or OLLAMA_API_KEY
    if effective_key:
        try:
            cloud_res = requests.post(
                OLLAMA_CLOUD_URL,
                headers={
                    "Authorization": f"Bearer {effective_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": OLLAMA_CLOUD_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                },
                timeout=30
            )
            if cloud_res.status_code == 200:
                raw_text = cloud_res.json().get("message", {}).get("content", "").strip()
                content, err = _parse_and_validate(raw_text)
                if content:
                    return content, None
        except Exception:
            pass

    # ── Attempt 3: Intelligent Offline Template Fallback ──
    normalized_topic = topic.strip().lower()
    for key, template in OFFLINE_TEMPLATES.items():
        if key in normalized_topic or normalized_topic in key:
            return template, None

    # Generic high quality fallback for unknown topics
    return {
        "headline": f"Protect Our Planet: Take Action on {topic.title()}",
        "message": f"Our environment is interconnected, and protecting {topic} ensures a healthier future for generations to come. Small sustainable actions today create lasting change.",
        "tips": [
            f"Raise awareness about {topic} among friends, family, and community",
            "Adopt mindful daily habits that conserve resources and reduce waste",
            "Support green initiatives and local sustainability efforts"
        ],
        "slogan": f"For Our Earth, For Our Future: Act on {topic.title()}!"
    }, None

