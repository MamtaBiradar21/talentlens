import os
from dotenv import load_dotenv

# OpenAI
from openai import OpenAI

# Gemini (NEW SDK)
from google import genai

load_dotenv()

# Load keys
openai_key = os.getenv("OPENAI_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

# Setup OpenAI client
openai_client = OpenAI(api_key=openai_key) if openai_key else None

# Setup Gemini client (NEW WAY)
gemini_client = genai.Client(api_key=gemini_key) if gemini_key else None


# -------------------------
# Prompt Builder
# -------------------------

def generate_prompt(resume_text, skills, best_match):
    return f"""
You are an expert AI Career Advisor.

Resume:
{resume_text}

Extracted Skills:
{skills}

Best Matched Role:
{best_match}

Provide:

1. Personalized improvement suggestions
2. Resume rewrite suggestions
3. Suggested certifications
4. Recommended projects

Keep response structured and professional.
"""


# -------------------------
# OpenAI
# -------------------------

def generate_with_openai(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional AI career coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content


# -------------------------
# Gemini (NEW SDK)
# -------------------------

def generate_with_gemini(prompt):
    response = gemini_client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    return response.text


# -------------------------
# Hybrid AI Logic
# -------------------------

def generate_career_suggestions(resume_text, skills, best_match):

    prompt = generate_prompt(resume_text, skills, best_match)

    # 1️⃣ Try OpenAI first
    if openai_client:
        try:
            print("Using OpenAI...")
            return generate_with_openai(prompt)
        except Exception as e:
            print("OpenAI failed:", e)

    # 2️⃣ Fallback to Gemini
    if gemini_client:
        try:
            print("Switching to Gemini...")
            return generate_with_gemini(prompt)
        except Exception as e:
            print("Gemini failed:", e)

    return "AI services are currently unavailable."