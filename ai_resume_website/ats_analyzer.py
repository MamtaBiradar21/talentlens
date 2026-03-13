import re
import requests

# ---------------- KEYWORD DENSITY ----------------
def keyword_density_score(resume_text, skills):
    resume_text = resume_text.lower()
    word_count = len(resume_text.split())

    if word_count == 0:
        return 0

    keyword_count = 0
    for skill in skills:
        keyword_count += resume_text.count(skill.lower())

    density = (keyword_count / word_count) * 100

    # Ideal density between 2% – 5%
    if 2 <= density <= 5:
        return 20
    elif 1 <= density < 2 or 5 < density <= 7:
        return 15
    else:
        return 8


# ---------------- SECTION DETECTION ----------------
def section_score(resume_text):
    sections = ["education", "experience", "skills", "projects", "certifications"]
    score = 0
    resume_text = resume_text.lower()

    for section in sections:
        if section in resume_text:
            score += 4  # 5 sections × 4 = 20

    return score


# ---------------- CONTACT VALIDATION ----------------
def contact_score(resume_text):
    score = 0

    email_pattern = r'\b[\w\.-]+@[\w\.-]+\.\w+\b'
    phone_pattern = r'\b\d{10}\b'

    if re.search(email_pattern, resume_text):
        score += 10

    if re.search(phone_pattern, resume_text):
        score += 10

    return score  # max 20


# ---------------- GRAMMAR CHECK ----------------
def grammar_score(resume_text):
    try:
        response = requests.post(
            "https://api.languagetool.org/v2/check",
            data={
                "text": resume_text,
                "language": "en-US"
            }
        )

        result = response.json()
        errors = len(result.get("matches", []))

        if errors < 5:
            return 20
        elif errors < 15:
            return 15
        else:
            return 8

    except:
        return 10  # fallback if API fails


# ---------------- LENGTH ANALYSIS ----------------
def length_score(resume_text):
    word_count = len(resume_text.split())

    # Ideal resume: 400 – 900 words
    if 400 <= word_count <= 900:
        return 20
    elif 250 <= word_count < 400 or 900 < word_count <= 1100:
        return 15
    else:
        return 8


# ---------------- FINAL ATS SCORE ----------------
def calculate_ats_score(resume_text, skills):
    scores = {}

    scores["keyword"] = keyword_density_score(resume_text, skills)
    scores["sections"] = section_score(resume_text)
    scores["contact"] = contact_score(resume_text)
    scores["grammar"] = grammar_score(resume_text)
    scores["length"] = length_score(resume_text)

    total_score = sum(scores.values())

    return total_score, scores