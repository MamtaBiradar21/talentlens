import os
import re
import csv
from collections import defaultdict
from sentence_transformers import SentenceTransformer, util
import string

# Load semantic model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Synonym mapping
SKILL_SYNONYMS = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "js": "javascript",
    "py": "python",
    "dl": "deep learning",
    "tf": "tensorflow"
}

# Skill categories
SKILL_CATEGORIES = {
    "python": "backend",
    "java": "backend",
    "flask": "backend",
    "django": "backend",
    "react": "frontend",
    "javascript": "frontend",
    "html": "frontend",
    "css": "frontend",
    "sql": "database",
    "mongodb": "database",
    "machine learning": "data",
    "deep learning": "data",
    "tensorflow": "data",
    "docker": "devops",
    "aws": "cloud"
}

def preprocess_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_experience(text, skill):
    # Matches patterns like "3 years Python", "2+ yrs of Python experience"
    pattern = rf'(\d+\+?)\s*(years|yrs|year)?\s*(of)?\s*{re.escape(skill)}'
    match = re.search(pattern, text)
    if match:
        return match.group(1) + " years"
    return None

def normalize_skills(skill_list):
    return [s.strip().lower() for s in skill_list]

def extract_skills(resume_text, job_skills=None):
    """
    Extract skills from resume_text and compute skills to improve based on job_skills.
    
    Parameters:
        resume_text (str): Full text of resume.
        job_skills (list of str): Skills required for the job (optional).
        
    Returns:
        dict with:
            skills: list of extracted skills
            categories: dict of skill categories
            experience: dict of skill: experience
            skills_to_improve: list of missing skills (if job_skills provided)
    """

    resume_text = preprocess_text(resume_text)

    # Load master skill list from CSV
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CSV_PATH = os.path.join(BASE_DIR, 'data', 'skills_list.csv')
    with open(CSV_PATH, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        skill_list = [row[0].strip().lower() for row in reader if row]

    # Apply synonyms in resume text
    for key, val in SKILL_SYNONYMS.items():
        resume_text = re.sub(rf'\b{re.escape(key)}\b', val, resume_text)

    skills_found = set()
    categorized_skills = defaultdict(list)
    experience_data = {}

    # --- Exact Match ---
    for skill in skill_list:
        if re.search(rf'\b{re.escape(skill)}\b', resume_text):
            skills_found.add(skill)

    # --- Semantic Matching ---
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    for skill in skill_list:
        if skill in skills_found:
            continue  # Already found via exact match
        skill_embedding = model.encode(skill, convert_to_tensor=True)
        similarity = util.cos_sim(resume_embedding, skill_embedding)
        if similarity.item() > 0.65:
            skills_found.add(skill)

    # Categorization + Experience
    for skill in skills_found:
        category = SKILL_CATEGORIES.get(skill, "other")
        categorized_skills[category].append(skill)
        exp = extract_experience(resume_text, skill)
        if exp:
            experience_data[skill] = exp

    # --- Skills to Improve ---
    skills_to_improve = []
    if job_skills:
        job_skills_normalized = [SKILL_SYNONYMS.get(s.lower(), s.lower()) for s in job_skills]
        for js in job_skills_normalized:
            if js not in skills_found:
                skills_to_improve.append(js)

    return {
        "skills": sorted(list(skills_found)),
        "categories": dict(categorized_skills),
        "experience": experience_data,
        "skills_to_improve": skills_to_improve
    }