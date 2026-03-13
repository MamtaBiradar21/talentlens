import pandas as pd

def match_jobs(extracted_skills):
    import os
    import pandas as pd

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, "data", "job_descriptions.csv")

    df = pd.read_csv(csv_path)

    results = []

    for _, row in df.iterrows():
        job_role = row["job_role"]
        job_skills = [s.strip().lower() for s in row["skills"].split(",")]

        matched = set(extracted_skills) & set(job_skills)
        if job_skills and extracted_skills:
           precision = len(matched) / len(extracted_skills)
           recall = len(matched) / len(job_skills)
    
           if precision + recall > 0:
             score = (2 * precision * recall) / (precision + recall) * 100
           else:
             score = 0
        else:
          score = 0

        missing = list(set(job_skills) - set(extracted_skills))

        results.append({
            "role": job_role,
            "score": round(score, 2),
            "matched_skills": list(matched),
            "missing_skills": missing
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results