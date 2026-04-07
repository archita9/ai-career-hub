import PyPDF2
import re

SKILLS_MAP = {
    "Machine Learning": ["python", "numpy", "pandas", "scikit-learn", "tensorflow", "pytorch", "keras", "deep learning", "nlp", "computer vision", "mlops"],
    "Data Science": ["python", "sql", "pandas", "numpy", "statistics", "tableau", "powerbi", "data visualization", "r", "hadoop", "spark"],
    "Web Development": ["html", "css", "javascript", "react", "node", "angular", "vue", "django", "flask", "mongodb", "postgresql", "figma", "ui/ux"],
    "Software Developer": ["java", "c++", "c#", "dsa", "git", "docker", "kubernetes", "linux", "aws", "azure", "system design"]
}

ALL_SKILLS = [skill for skills in SKILLS_MAP.values() for skill in skills]

def parse_resume(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text().lower()

    # Extract CGPA
    cgpa_match = re.search(r'(?:cgpa|gpa|percentage)[:\s]+([0-9]*\.?[0-9]+)', text)
    cgpa = float(cgpa_match.group(1)) if cgpa_match else 0.0
    if cgpa > 10.0: cgpa = cgpa / 10.0

    # Improved Skill Extraction with Word Boundaries
    found_set = set()
    for skill in set(ALL_SKILLS):
        # Use regex to find whole words, handle skills with special characters like ++ or #
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_set.add(skill)
    
    skills_found = list(found_set)
    
    # Calculate ATS Score
    ats_score = min(len(skills_found) * 8 + len(re.findall(r'project|experience|internship', text)) * 6, 100)
    
    # Portfolio Health
    links = re.findall(r'github\.com|linkedin\.com|http[s]?://[^\s]+', text)
    portfolio_health = min(len(links) * 20, 100)

    # Detect Likely Domain
    domain_scores = {}
    for domain, skills in SKILLS_MAP.items():
        score = 0
        for s in skills:
            if re.search(r'\b' + re.escape(s) + r'\b', text, re.IGNORECASE):
                score += 1
        domain_scores[domain] = score
    
    detected_domain = max(domain_scores, key=domain_scores.get)

    return {
        "skills_found": skills_found,
        "skills_count": len(skills_found),
        "internships": len(re.findall(r'internship|intern\b', text)),
        "projects": len(re.findall(r'project\b', text)),
        "cgpa": cgpa,
        "ats_score": ats_score,
        "portfolio_health": portfolio_health,
        "links": links,
        "detected_domain": detected_domain
    }

