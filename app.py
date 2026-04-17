import streamlit as st
import pickle
import numpy as np
import pandas as pd
import sqlite3
import hashlib
import os
import time
import datetime
import re
from dotenv import load_dotenv
from resume_parser import parse_resume
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq Client
# To set your key securely via terminal on Windows, run: setx GROQ_API_KEY "your_actual_key"
# Then RESTART your terminal/IDE for changes to take effect.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

def render_groq_status():
    if not GROQ_API_KEY:
        with st.expander("🔑 Groq API Key is not set!", expanded=False):
            st.markdown("""
            ### How to set your key securely:
            1. Open your terminal (PowerShell or CMD).
            2. Run the following command:
               ```bash
               setx GROQ_API_KEY "your_groq_api_key_here"
               ```
            3. **Restart your IDE (VS Code) and terminal** to apply the change.
            4. Once set, the key will be stored in your system and won't appear in the code!
            """)


# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Placement Pro AI | Career Ecosystem",
    page_icon="🐼",
    layout="wide",
)

# =========================
# DATA MODELS
# =========================
ROLE_INFO = {
    "Machine Learning": {
        "skills": ["python", "numpy", "pandas", "scikit-learn", "tensorflow", "pytorch"],
        "roadmap": {
            "Beginner": {"topics": ["Math for ML", "Python Basics"], "project": "Titanic Predictor", "improvement": "Add cross-validation."},
            "Intermediate": {"topics": ["Supervised Learning", "Git"], "project": "Customer Churn", "improvement": "Deploy it using Flask."},
            "Advanced": {"topics": ["MLOps", "Deployment"], "project": "Object Detection", "improvement": "Optimize using TensorRT."}
        },
        "companies": [{"name": "NVIDIA (Bangalore)", "lat": 12.9716, "lon": 77.5946, "city": "Bangalore"}],
        "courses": [
            {"name": "Andrew Ng ML", "platform": "Coursera", "type": "Free Audit"},
            {"name": "Deep Learning Specialization", "platform": "Coursera", "type": "Paid"},
            {"name": "AI For Everyone", "platform": "Coursera", "type": "Free"}
        ],
        "youtube": ["Krish Naik", "Sentdex", "Andrej Karpathy"],
        "dsa": ["Heaps", "DP", "Linear Algebra Application", "Arrays"],
        "platforms": ["LinkedIn", "Kaggle Jobs", "AngelList"]
    },
    "Data Science": {
        "skills": ["python", "sql", "statistics", "tableau", "powerbi"],
        "roadmap": {
            "Beginner": {"topics": ["Excel", "SQL Basics"], "project": "Sales Dashboard", "improvement": "Automated data pipelines."},
            "Intermediate": {"topics": ["Data Cleaning", "Tableau"], "project": "Stock Visualizer", "improvement": "Time-series forecasting."},
            "Advanced": {"topics": ["Predictive Modeling", "Big Data"], "project": "Fraud Detection", "improvement": "Anomaly Detection."}
        },
        "companies": [{"name": "Fractal Analytics", "lat": 19.0760, "lon": 72.8777, "city": "Mumbai"}],
        "courses": [
            {"name": "Google Data Analytics", "platform": "Coursera", "type": "Paid"},
            {"name": "IBM Data Science", "platform": "Coursera", "type": "Paid"},
            {"name": "SQL for Data Science", "platform": "Udemy", "type": "Paid"}
        ],
        "youtube": ["StatQuest", "Luke Barousse", "Alex The Analyst"],
        "dsa": ["SQL Joins", "Searching/Sorting", "Complex Queries"],
        "platforms": ["LinkedIn", "Naukri", "Indeed"]
    },
    "Web Development": {
        "skills": ["html", "css", "javascript", "react", "node", "mongodb"],
        "roadmap": {
            "Beginner": {"topics": ["HTML5/CSS3", "JS"], "project": "Portfolio", "improvement": "Optimize for SEO/Speed."},
            "Intermediate": {"topics": ["React.js", "REST APIs"], "project": "E-commerce", "improvement": "Add Stripe integration."},
            "Advanced": {"topics": ["Next.js", "Web Cache"], "project": "SaaS App", "improvement": "Clerk/NextAuth integration."}
        },
        "companies": [{"name": "Swiggy (Bangalore)", "lat": 12.9716, "lon": 77.5946, "city": "Bangalore"}],
        "courses": [
            {"name": "The Odin Project", "platform": "Web", "type": "Free"},
            {"name": "JavaScript Mastery Pro", "platform": "JSMastery", "type": "Paid"},
            {"name": "Full Stack Open", "platform": "Uni Helsinki", "type": "Free"}
        ],
        "youtube": ["Traversy Media", "Web Dev Simplified", "Hitesh Choudhary"],
        "dsa": ["Trees", "Graphs", "Recursion", "Strings"],
        "platforms": ["LinkedIn", "Internshala", "HackerRank"]
    },
    "Software Developer": {
        "skills": ["java", "c++", "dsa", "git", "system design"],
        "roadmap": {
            "Beginner": {"topics": ["Logic", "Git"], "project": "Bank System", "improvement": "Unit testing."},
            "Intermediate": {"topics": ["DSA", "OS"], "project": "Web Server", "improvement": "Socket programming."},
            "Advanced": {"topics": ["System Design", "Microservices"], "project": "Chat App", "improvement": "Scalable message queue."}
        },
        "companies": [{"name": "Amazon R&D", "lat": 13.0827, "lon": 80.2707, "city": "Chennai"}],
        "courses": [
            {"name": "CS50 Harvard", "platform": "edX", "type": "Free"},
            {"name": "AlgoExpert", "platform": "AlgoExpert.io", "type": "Paid"},
            {"name": "System Design Interview", "platform": "ByteByteGo", "type": "Paid"}
        ],
        "youtube": ["Striver (takeUforward)", "Clement", "Abdul Bari"],
        "dsa": ["DP", "Graphs", "Bit Manipulation", "Trees"],
        "platforms": ["LinkedIn", "Naukri", "LeetCode Jobs"]
    }
}

LIVE_CONTESTS = {
    "Hackathons": [
        {"name": "Smart India Hackathon 2024", "plus": "Biggest Govt hackathon with live Ministry problems.", "mode": "Offline", "reward": "₹1 Lakh"},
        {"name": "Flipkart GRID 6.0", "plus": "Major tech challenge for engineering students.", "mode": "Online", "reward": "PPOs + ₹5 Lakh"},
        {"name": "HackerRank Holi Cup", "plus": "Best for freshers to get a global rank badge.", "mode": "Remote", "reward": "Swag"}
    ],
    "Kaggle": [
        {"name": "Spaceship Titanic", "plus": "Perfect for ML Resume - easy for interviews.", "mode": "Remote", "reward": "$50k"},
        {"name": "Store Sales Forecast", "plus": "Handles real-world time-series data.", "mode": "Remote", "reward": "Knowledge"},
        {"name": "Digit Recognizer", "plus": "Standard entry-level Computer Vision challenge.", "mode": "Remote", "reward": "Expert Badge"}
    ],
    "Unstop": [
        {"name": "Reliance TUP 9.0", "plus": "Direct entry to Reliance leadership interviews.", "mode": "Mixed", "reward": "₹10 Lakh"},
        {"name": "Tata Imagination 2024", "plus": "Showcase strategic thinking for leadership roles.", "mode": "Remote", "reward": "Internships"},
        {"name": "Amazon ML Summer School", "plus": "Top-tier mentorship from Amazon scientists.", "mode": "Remote", "reward": "Amazon Internships"}
    ]
}

INTERNSHIPS = [
    # Machine Learning
    {"name": "NVIDIA AI", "role": "Applied Scientist Intern", "field": "Machine Learning", "lat": 12.9850, "lon": 77.5946, "city": "Bangalore, KA", "deadline": "Active"},
    {"name": "Microsoft ML", "role": "Research Intern", "field": "Machine Learning", "lat": 17.4474, "lon": 78.3762, "city": "Hyderabad, TS", "deadline": "Open Now"},
    {"name": "Google AI Hub", "role": "ML Intern", "field": "Machine Learning", "lat": 12.9716, "lon": 77.5946, "city": "Bangalore, KA", "deadline": "Apply Soon"},
    {"name": "Amazon AWS", "role": "ML Engineer Intern", "field": "Machine Learning", "lat": 18.5204, "lon": 73.8567, "city": "Pune, MH", "deadline": "Rolling"},
    {"name": "Tesla Autopilot", "role": "Vision Intern", "field": "Machine Learning", "lat": 28.6139, "lon": 77.2090, "city": "Delhi, DL", "deadline": "Waitlist"},

    # Data Science
    {"name": "Fractal Data", "role": "Data Analyst Intern", "field": "Data Science", "lat": 19.0760, "lon": 72.8777, "city": "Mumbai, MH", "deadline": "Rolling"},
    {"name": "Mu Sigma", "role": "Decision Scientist", "field": "Data Science", "lat": 12.9716, "lon": 77.5946, "city": "Bangalore, KA", "deadline": "Active"},
    {"name": "IBM Watson", "role": "Data Insights Intern", "field": "Data Science", "lat": 28.4595, "lon": 77.0266, "city": "Gurgaon, HR", "deadline": "Open"},
    {"name": "JP Morgan", "role": "Quantitative Analyst", "field": "Data Science", "lat": 17.4474, "lon": 78.3762, "city": "Hyderabad, TS", "deadline": "Closing Soon"},
    {"name": "American Express", "role": "Risk Analyst", "field": "Data Science", "lat": 28.4595, "lon": 77.0266, "city": "Gurgaon, HR", "deadline": "Apply Now"},

    # Web Development
    {"name": "Zomato Frontend", "role": "Web Dev Intern", "field": "Web Development", "lat": 28.4595, "lon": 77.0266, "city": "Gurgaon, HR", "deadline": "Apply Now"},
    {"name": "Swiggy App", "role": "FullStack Intern", "field": "Web Development", "lat": 12.9716, "lon": 77.5946, "city": "Bangalore, KA", "deadline": "Rolling"},
    {"name": "BrowserStack", "role": "Web Engineering Intern", "field": "Web Development", "lat": 19.1176, "lon": 72.8631, "city": "Mumbai, MH", "deadline": "Active"},
    {"name": "Vercel India", "role": "Frontend Intern", "field": "Web Development", "lat": 12.9141, "lon": 77.5946, "city": "Bangalore, KA", "deadline": "Open Soon"},
    {"name": "Postman Dev", "role": "Web Tools Intern", "field": "Web Development", "lat": 12.9716, "lon": 77.5946, "city": "Bangalore, KA", "deadline": "Active"},

    # Software Developer
    {"name": "Google Step", "role": "SDE Intern", "field": "Software Developer", "lat": 12.9716, "lon": 77.5946, "city": "Bangalore, KA", "deadline": "Apply Soon"},
    {"name": "Flipkart Tech", "role": "SDE Intern", "field": "Software Developer", "lat": 12.9341, "lon": 77.6101, "city": "Bangalore, KA", "deadline": "Apply Soon"},
    {"name": "Razorpay SDE", "role": "SDE Intern", "field": "Software Developer", "lat": 12.9141, "lon": 77.5946, "city": "Bangalore, KA", "deadline": "Closing Soon"},
    {"name": "Oracle Dev", "role": "SDE Intern", "field": "Software Developer", "lat": 17.4474, "lon": 78.3762, "city": "Hyderabad, TS", "deadline": "Rolling"},
    {"name": "Amazon R&D", "role": "Software Intern", "field": "Software Developer", "lat": 13.0827, "lon": 80.2707, "city": "Chennai, TN", "deadline": "Active"}
]

# =========================
# SESSION STATE
# =========================
if 'theme' not in st.session_state: st.session_state.theme = 'dark'
if 'user' not in st.session_state: st.session_state.user = None
if 'resume_data' not in st.session_state: st.session_state.resume_data = None
if 'portfolio_url' not in st.session_state: st.session_state.portfolio_url = ""
if 'timer_start' not in st.session_state: st.session_state.timer_start = None
if 'queens' not in st.session_state: st.session_state.queens = [-1] * 4

# =========================
# UI
# =========================
def apply_theme():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
            html, body, [class*="css"] {
                font-family: 'Outfit', sans-serif !important;
            }
            .stApp {
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                color: #f8fafc;
            }
            .main-card {
                background: rgba(30, 41, 59, 0.4);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
                margin-bottom: 24px;
                color: #f8fafc;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .main-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
            }
            a.dynamic-link { color: #38bdf8 !important; text-decoration: none !important; font-weight: 500; }
            a.dynamic-link:hover { text-decoration: underline !important; color: #bae6fd !important; }
            .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.3s ease; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("<div style='position:fixed; top:15px; right:20px; font-size:40px; z-index:1000;'>🐼</div>", unsafe_allow_html=True)

apply_theme()

# =========================
# DB
# =========================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def log_activity(action_type, description):
    if st.session_state.user:
        try:
            db = get_db()
            db.execute("INSERT INTO activity_log (user_id, action_type, description) VALUES (?, ?, ?)", 
                       (st.session_state.user['id'], action_type, description))
            db.commit()
            db.close()
        except:
            pass

# =========================
# ✨ DREAM QUEST
# =========================
def dream_quest():
    st.markdown("# ✨ The Dream Quest")
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.subheader("🚩 Phase 2: Define your North Star")
    dream_corp = st.text_input("Enter your Dream Company (e.g. Google, Tesla):")
    dream_role = st.text_input("Enter your Target Major Role (e.g. Architect, Lead Scientist):")
    
    if dream_corp and dream_role:
        st.success(f"Objective Set: {dream_role} at {dream_corp}")
        log_activity("Dream Quest", f"Target set: {dream_role} at {dream_corp}")
        st.write("### ➕ Achievement Delta (Strict Steps):")
        st.markdown("- **Step 1**: Master System Design for high-load systems.")
        st.markdown(f"- **Step 2**: Contribute to 2 high-impact Open Source projects used by {dream_corp}.")
        st.markdown("- **Step 3**: Conduct a 'Deep Company Research' and cold-email a senior lead at the company.")
        st.markdown("- **Step 4**: Complete the specialized certification listed for this role in the Roadmap.")
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# LAUNCHPAD
# =========================
def launchpad_pro(role):
    st.markdown("# 🚀 Mastery Launchpad (Fresher Pro)")
    st.write("The 'Plus Factors' that every fresher needs to know.")
    
    # Hero Card
    st.markdown("""<div style='background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%); padding: 30px; border-radius: 12px; margin-bottom: 20px; text-align:center;'>
    <h2 style='color:white; margin:0;'>✨ From Zero to Industry Pro</h2>
    <p style='color:white; opacity:0.9;'>Everything you MUST know about GitHub, LinkedIn, and Strategy.</p></div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("<div class='main-card' style='border-top: 5px solid #38bdf8;'>", unsafe_allow_html=True)
        st.subheader("🐙 GitHub Mastery")
        st.write("- **Pin Top 3 Repos**: Must have a valid GIF/Image demo.")
        st.write("- **Green Streak**: Aim for 3 commits/week.")
        st.write("- **Follow-up**: Contribute to open source libraries.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='main-card' style='border-top: 5px solid #818cf8;'>", unsafe_allow_html=True)
        st.subheader("🔗 LinkedIn Branding")
        st.write("- **Headline**: Target Role + Top Tech Stack.")
        st.write("- **Cold Messaging**: Message 5 HRs daily with a note.")
        st.write("- **Apps**: LinkedIn, Internshala, Naukri.com.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c3:
        st.markdown("<div class='main-card' style='border-top: 5px solid #fbbf24;'>", unsafe_allow_html=True)
        st.subheader("📊 DSA Strategy")
        st.write("- **Must-Do**: " + ", ".join(ROLE_INFO[role]['dsa']))
        st.write("- **Solve Daily**: Minimum 2 LeetCode Mediums.")
        st.write("- **Follow-up**: Send 'Thank You' notes after any viva.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📽️ Expert YouTubers (Follow for " + role + ")")
    y1, y2, y3 = st.columns(3)
    yt_list = ROLE_INFO[role]['youtube']
    for i, name in enumerate(yt_list):
        with [y1, y2, y3][i % 3]:
            st.markdown(f"<div style='background:rgba(255,0,0,0.1); padding:15px; border-radius:10px; border-left:4px solid red; margin-bottom:10px;'>🎥 <b>{name}</b></div>", unsafe_allow_html=True)

    st.divider()
    st.write("### 💡 Proven job search practices:")
    st.info("Directly 'Calling HR' or cold-emailing with your ATS score is a major 'Plus' over 90% of applicants who just 'Easy Apply'. Deep research on company products wins interviews.")

# =========================
# GAME ZONE
# =========================
def game_zone():
    import requests
    st.markdown("## 🎮 Skill Gaming & Streaks")
    
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    st.markdown("### 🐙 GitHub Activity Sync")
    gh_user_input = st.text_input("Enter your GitHub Username (or profile link) to auto-sync:", key="gh_username_sync")
    gh_commits_today = False
    
    if gh_user_input:
        # Extract username if the user pastes a full URL
        gh_user = gh_user_input.strip()
        if "github.com/" in gh_user:
            gh_user = gh_user.split("github.com/")[-1].strip("/")
            gh_user = gh_user.split("/")[0]  # Just take the username part
            
        with st.spinner(f"Connecting to GitHub API for @{gh_user}..."):
            try:
                res = requests.get(f"https://api.github.com/users/{gh_user}/events/public", timeout=5)
                if res.status_code == 200:
                    events = res.json()
                    today_str = datetime.datetime.utcnow().strftime('%Y-%m-%d')
                    
                    push_count = 0
                    for e in events:
                        if e.get('type') == 'PushEvent' and e.get('created_at', '').startswith(today_str):
                            push_count += len(e.get('payload', {}).get('commits', []))
                    
                    if push_count > 0:
                        gh_commits_today = True
                        st.success(f"Awesome! Verified {push_count} public commits today from **{gh_user}**. 'Git commit' task auto-completed! ✅")
                    else:
                        import subprocess
                        try:
                            git_out = subprocess.check_output(["git", "log", "--since=midnight", "--oneline"], stderr=subprocess.DEVNULL).decode("utf-8")
                            local_commits = len([line for line in git_out.strip().split('\n') if line])
                            if local_commits > 0:
                                gh_commits_today = True
                                st.success(f"No public commits found, but verified **{local_commits} local commits** in your current project today! 'Git commit' task auto-completed! ✅")
                            else:
                                st.warning(f"No public or local commits found today. (Note: GitHub API only shows public pushes!). Keep coding!")
                        except Exception:
                            st.warning(f"No public commits found today for **{gh_user}**. (Note: GitHub API only shows public pushes!). Keep coding!")
                else:
                    st.error("Invalid GitHub username or API limit reached.")
            except:
                st.error("Failed to connect to GitHub API.")
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.subheader("🔥 Daily Placement Streak")
        st.info("💡 **How to play:** Check the boxes as you complete your daily career tasks. Complete all 12 tasks to earn your daily trophy and maintain your momentum!")
        itms = ["Apply to job", "Cold email HR", "Study Theory", "Project work", "Git commit", "LinkedIn post", "Email reading", "Company Search", "Mock Test", "DSA Solve", "Portfolio fix", "Networking"]
        done = 0
        for i, itm in enumerate(itms):
            is_git_task = (itm == "Git commit")
            if is_git_task and gh_commits_today:
                st.checkbox(itm + " 🐙 (Verified)", value=True, key=f"streak_gh_{i}", disabled=True)
                done += 1
            else:
                if st.checkbox(itm, key=f"streak_{i}"):
                    done += 1
        st.progress(done / len(itms))
        st.write(f"Status: **{done} / {len(itms)}** streak complete")
        if done >= len(itms): 
            st.markdown("<h2 style='text-align:center;'>🏆 Trophy Unlocked!</h2>", unsafe_allow_html=True)
            st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.subheader("👑 4-Queens Mind Game")
        with st.expander("📖 How to Play"):
            st.write("""
            **Goal:** Place 4 queens on the 4x4 grid such that no two queens threaten each other.
            
            **Rules:**
            1. No two queens can be in the same **row**.
            2. No two queens can be in the same **column**.
            3. No two queens can be on the same **diagonal**.
            
            **How to move:** Click on a square in each column to place a queen. A '♛' represents a queen.
            """)
        
        grid = st.columns(4)
        for c in range(4):
            for r in range(4):
                is_q = st.session_state.queens[c] == r
                if grid[c].button("♛" if is_q else "□", key=f"qg_{r}_{c}"):
                    st.session_state.queens[c] = r
                    st.rerun()
        
        # Win Check
        def check_win(q):
            if -1 in q: return False
            for i in range(4):
                for j in range(i+1, 4):
                    if q[i] == q[j] or abs(q[i]-q[j]) == abs(i-j): return False
            return True
            
        if check_win(st.session_state.queens):
            st.success("🎉 You Win! Mind Freshened!")
            st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)

# =========================
# STUDENT HUB
# =========================
def student_hub():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧭 Navigation")
    pages = [
        "📊 AI Analysis",
        "✨ Dream Quest",
        "🛣️ Career Roadmap",
        "🏆 Live Contests",
        "💼 Internships",
        "🚀 Mastery Launchpad",
        "🎮 Game Zone",
        "🎙️ AI Career Copilot",
        "🕒 Activity History"
    ]
    if st.session_state.user.get('role') == 'Admin / Developer':
        pages.append("🛠️ Developer Copilot")
    selection = st.sidebar.radio("Go to:", pages, label_visibility="collapsed")
    st.sidebar.markdown("---")
    
    if selection == "📊 AI Analysis":
        st.markdown("<h2 style='color:#38bdf8;'>Phase 1: Resume Analysis</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("<div class='main-card'>", unsafe_allow_html=True)
            st.subheader("📄 Upload Resume")
            uploaded = st.file_uploader("Upload Document (PDF)", type=["pdf"], key="analysis_up")
            if uploaded:
                st.session_state.resume_data = parse_resume(uploaded)
                data = st.session_state.resume_data
                st.success("Analysis Complete!")
                log_activity("Resume Analysis", f"Analyzed resume. ATS Score: {data['ats_score']}%")
                c1, c2 = st.columns(2)
                c1.metric("ATS Match", f"{data['ats_score']}%")
                c2.metric("Portfolio Health", f"{data['portfolio_health']}%")
                st.divider()
                st.session_state.portfolio_url = st.text_input("Enter Portfolio Link:", value=st.session_state.portfolio_url)
                st.subheader("💡 Improvement Suggestions")
                st.write("- Focus on adding 2+ scalable projects.")
                st.write("- Optimize skills section for ATS keywords.")
                st.subheader("📬 Follow-up")
                st.info("Directly cold-email the Hiring Manager noting your ATS score.")
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            if st.session_state.resume_data:
                data = st.session_state.resume_data
                st.markdown("<div class='main-card'>", unsafe_allow_html=True)
                st.subheader("🎯 Skill Gap Check")
                role = st.selectbox("Compare Role Target:", list(ROLE_INFO.keys()))
                req = ROLE_INFO[role]['skills']
                found = data['skills_found']
                missing = list(set(req) - set(found))
                m1, m2 = st.columns(2)
                with m1:
                    st.write("**Identified ✅**")
                    for s in found: 
                        if s in req: st.success(s)
                with m2:
                    st.write("**Missing 🔥**")
                    for s in missing: st.error(s)
                st.markdown("</div>", unsafe_allow_html=True)

    elif selection == "✨ Dream Quest":
        dream_quest()
    
    elif selection == "🛣️ Career Roadmap":
        role = st.selectbox("Select Pathway Filter:", list(ROLE_INFO.keys()), key="rm_sel_hub")
        st.markdown(f"## 🛣️ {role} Pathway")
        st.write("### 📚 Recommended Courses (Free & Paid)")
        for crs in ROLE_INFO[role]['courses']:
            search_query = f"{crs['name']} {crs['platform']}".replace(' ', '%20')
            st.markdown(f"<div class='main-card'><b>{crs['name']}</b> ({crs['platform']}) - <i>{crs['type']}</i> <br><br> <a class='dynamic-link' href='https://www.google.com/search?q={search_query}' target='_blank'>🔗 Go to Course</a></div>", unsafe_allow_html=True)
        
        rm = ROLE_INFO[role]['roadmap']
        cc1, cc2, cc3 = st.columns(3)
        for i, level in enumerate(["Beginner", "Intermediate", "Advanced"]):
            with [cc1, cc2, cc3][i]:
                st.markdown(f"<div class='main-card'>", unsafe_allow_html=True)
                st.subheader(level)
                for t in rm[level]['topics']: st.write(f"• {t}")
                st.success(f"🚀 {rm[level]['project']}")
                st.markdown("</div>", unsafe_allow_html=True)

    elif selection == "🏆 Live Contests":
        st.markdown("## 🏆 Live Contests & Hackathons")
        for cat, items in LIVE_CONTESTS.items():
            st.subheader(cat)
            for itm in items:
                search_query = f"{itm['name']} Hackathon".replace(' ', '%20')
                st.markdown(f"<div class='main-card'><b>{itm['name']}</b><br>Plus Overview: {itm['plus']}<br>Prizes: {itm['reward']} | Mode: {itm['mode']} <br><br> <a class='dynamic-link' href='https://www.google.com/search?q={search_query}' target='_blank'>🔗 Link to Register</a></div>", unsafe_allow_html=True)
        
        if st.button("✨ Fetch Live AI Contest Recommendations"):
            with st.spinner("Analyzing live tech landscape..."):
                prompt = "List 5 major upcoming global coding contests or hackathons for 2024-2025. Include Name, Category, and a brief 'Plus Factor' explaining why students should join. Format as a clean list."
                if not client:
                    st.error("Groq client not initialized. Please check your API key.")
                else:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.1-8b-instant",
                        )
                        st.markdown(f"<div class='main-card' style='border-left:5px solid #818cf8;'>{chat_completion.choices[0].message.content}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Groq API Error: {str(e)}")

    elif selection == "💼 Internships":
        st.markdown("## 💼 Internship opportunities")
        f = st.radio("Field Filter:", ["All"] + list(ROLE_INFO.keys()), horizontal=True)
        disp = [i for i in INTERNSHIPS if f == "All" or i['field'] == f]
        st.map(pd.DataFrame(disp))
        for i in disp: 
            search_query = f"{i['name']} {i['role']} internship".replace(' ', '%20')
            st.markdown(f"<div class='main-card'><b>{i['role']} @ {i['name']}</b> ({i['city']}) <br><br> <a class='dynamic-link' href='https://www.linkedin.com/jobs/search/?keywords={search_query}' target='_blank'>🔗 Apply / Search on LinkedIn</a></div>", unsafe_allow_html=True)
        
        if st.button("🚀 Find Live AI Internships (Powered by Groq)"):
            with st.spinner("Searching for top-tier opportunities..."):
                prompt = f"List 5 high-impact internship programs currently active or opening soon for the '{f}' domain (or general Tech if 'All'). Include Company, Role, and a quick tip on how to stand out. Format as a clean list."
                if not client:
                    st.error("Groq client not initialized. Please check your API key.")
                else:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.1-8b-instant",
                        )
                        st.markdown(f"<div class='main-card' style='border-left:5px solid #38bdf8;'>{chat_completion.choices[0].message.content}</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Groq API Error: {str(e)}")

    elif selection == "🚀 Mastery Launchpad":
        launchpad_pro(st.session_state.resume_data.get('detected_domain', 'Software Developer') if st.session_state.resume_data else "Software Developer")
    
    elif selection == "🎮 Game Zone":
        game_zone()

    elif selection == "🎙️ AI Career Copilot":
        st.markdown("## 🎙️ AI Career Copilot & Subscription Hub")
        v1, v2 = st.tabs(["💬 Career Chatbot", "💳 Membership Plans"])
        with v1:
            if st.session_state.timer_start is None:
                if st.button("Start Free AI Session (60s)"):
                    st.session_state.timer_start = time.time()
                    st.rerun()
            else:
                rem = 60 - int(time.time() - st.session_state.timer_start)
                if rem > 0:
                    st.info(f"⏳ Free Session Active: **{rem}s left**")
                    if 'messages' not in st.session_state: st.session_state.messages = []
                    for message in st.session_state.messages:
                        with st.chat_message(message["role"]): st.markdown(message["content"])
                    if prompt := st.chat_input("Ask about your roadmap or dream job..."):
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        with st.chat_message("user"): st.markdown(prompt)
                        
                        # AI Response via Groq
                        with st.chat_message("assistant"):
                            with st.spinner("Panda is thinking..."):
                                if not client:
                                    st.error("Groq client not initialized. Please check your API key.")
                                else:
                                    try:
                                        # Prepare context for better answers
                                        user_role = st.session_state.user.get('role', 'Student')
                                        resume_msg = f" User skills: {', '.join(st.session_state.resume_data['skills_found'])}" if st.session_state.resume_data else ""
                                        
                                        chat_completion = client.chat.completions.create(
                                            messages=[
                                                {"role": "system", "content": f"You are Panda Copilot, an expert career advisor. Be concise, encouraging, and provide industry-specific advice. User Context: {user_role}.{resume_msg}"},
                                                {"role": "user", "content": prompt}
                                            ],
                                            model="llama-3.1-8b-instant",
                                        )
                                        resp = chat_completion.choices[0].message.content
                                        st.markdown(resp)
                                        st.session_state.messages.append({"role": "assistant", "content": resp})
                                    except Exception as e:
                                        error_msg = f"Groq API Error: {str(e)}"
                                        st.error(error_msg)
                else:
                    st.warning("⚠️ Session Over. Upgrade to 'AI Plus' to continue chatting.")
                    if st.button("Reset Session"):
                        st.session_state.timer_start = None
                        st.session_state.messages = []
                        st.rerun()
        with v2:
            st.subheader("💎 Professional Subscription Tiers")
            s1, s2, s3 = st.columns(3)
            with s1: st.markdown("<div class='main-card'><h4>AI Plus</h4><p>₹60 / 10 mins</p></div>", unsafe_allow_html=True)
            with s2: st.markdown("<div class='main-card'><h4>Industry Mentor</h4><p>₹499 / session</p></div>", unsafe_allow_html=True)
            with s3: st.markdown("<div class='main-card'><h4>Executive/HR</h4><p>₹999 / session</p></div>", unsafe_allow_html=True)
            st.divider()
            st.info("UPI: **architagoyal7@okicici**")
            st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=upi://pay?pa=architagoyal7@okicici", width=150)

    elif selection == "🕒 Activity History":
        st.markdown("## 🕒 Activity History")
        st.markdown("<p style='color:#94a3b8;'>Your recent actions across the Placement Pro ecosystem.</p>", unsafe_allow_html=True)
        try:
            db = get_db()
            logs = db.execute("SELECT action_type, description, timestamp FROM activity_log WHERE user_id=? ORDER BY timestamp DESC LIMIT 20", (st.session_state.user['id'],)).fetchall()
            db.close()
            
            if logs:
                for log in logs:
                    st.markdown(f"""
                        <div style='background-color:#1e293b; padding:15px; border-radius:8px; border-left:4px solid #38bdf8; margin-bottom:10px;'>
                            <small style='color:#94a3b8;'>{log['timestamp']} • <b>{log['action_type']}</b></small><br>
                            <span style='color:#e2e8f0;'>{log['description']}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No activity recorded yet! Start by analyzing your resume or setting a Dream Quest.")
        except Exception as e:
            st.error("Could not load history. Please initialize the database.")

    elif selection == "🛠️ Developer Copilot":
        import json
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown("## 🛠️ Developer Copilot")
        with c2:
            if st.button("➕ New Chat"):
                st.session_state.dev_messages = []
                with open('admin_chat.json', 'w') as f:
                    json.dump([], f)
                st.rerun()

        st.info("This is an admin-exclusive LLM context that knows the codebase architecture.")
        try:
            with open("app.py", "r", encoding="utf-8") as f:
                code_content = f.read()
        except:
            code_content = "Code not available."
            
        if 'dev_messages' not in st.session_state: 
            try:
                with open('admin_chat.json', 'r') as f:
                    st.session_state.dev_messages = json.load(f)
            except:
                st.session_state.dev_messages = []
                
        for message in st.session_state.dev_messages:
            with st.chat_message(message["role"]): st.markdown(message["content"])
            
        if prompt := st.chat_input("Ask about the codebase, architecture, or potential changes..."):
            st.session_state.dev_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Analyzing project codebase..."):
                    if not client:
                        st.error("Groq client not initialized. Please check your API key.")
                    else:
                        try:
                            codebase_context = f"This is the source code of the project:\n\n```python\n{code_content[:6000]}\n```\n... (truncated). Explain code directly to the developer."
                            
                            api_messages = [{"role": "system", "content": f"You are a Developer Expert Assistant for the codebase. Answer queries based on the project code provided. Context: {codebase_context}"}]
                            for m in st.session_state.dev_messages[-10:]:
                                api_messages.append({"role": m["role"], "content": m["content"]})
                                
                            chat_completion = client.chat.completions.create(
                                messages=api_messages,
                                model="llama-3.1-8b-instant",
                            )
                            resp = chat_completion.choices[0].message.content
                            st.markdown(resp)
                            st.session_state.dev_messages.append({"role": "assistant", "content": resp})
                            
                            with open('admin_chat.json', 'w') as f:
                                json.dump(st.session_state.dev_messages, f)
                                
                        except Exception as e:
                            st.error(f"Groq API Error: {str(e)}")


# =========================
# GOOGLE AUTH WIDGET
# =========================
def render_google_button():# test change #test chnage
    client_id = "235907289435-nhbklhsa8rr75nai60mi5e8cmmteabqf.apps.googleusercontent.com"
    redirect_uri = "http://localhost:8501"
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=email%20profile"
    
    html_code = f"""
        <a href="{auth_url}" target="_self" style="text-decoration: none;">
            <div style="font-family: Arial, sans-serif; display: flex; align-items: center; justify-content: center; background-color: white; color: #555; border: 1px solid #ddd; border-radius: 8px; padding: 10px; cursor: pointer; font-weight: bold; transition: background-color 0.3s; margin-top: 10px; margin-bottom: 20px;">
                <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" style="width: 20px; margin-right: 10px;" />
                Continue with Google
            </div>
        </a>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# =========================
# MAIN
# =========================
def main():
    # Handle Google Auth Callback (Mock backend validation since Client Secret is not provided)
    if "code" in st.query_params:
        st.session_state.user = {"id": 999, "username": "Google User", "role": "Student"}
        st.query_params.clear()
        st.rerun()

    if not st.session_state.user:
        # Centered layout using Streamlit columns
        _, col_main, _ = st.columns([1, 1.5, 1])
        
        with col_main:
            st.markdown("<br><h1 style='text-align: center; color:#38bdf8; font-size: 3rem;'>🐼 Placement Pro AI</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color:#94a3b8; font-size: 1.1rem; margin-bottom: 30px;'>Sign in to access your AI Career Ecosystem</p>", unsafe_allow_html=True)
            
            # The Main Login Card wrapper
            st.markdown("<div style='background-color:#1e293b; padding:2rem; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155;'>", unsafe_allow_html=True)
            tab_l, tab_s = st.tabs(["🔐 Login", "📝 Sign Up"])
            
            with tab_l:
                st.markdown("<br>", unsafe_allow_html=True)
                u = st.text_input("Username", key="l_u")
                p = st.text_input("Password", type="password", key="l_p")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Log In", key="l_btn", use_container_width=True):
                    db = get_db()
                    u_row = db.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
                    if u_row and u_row['password'] == hashlib.sha256(p.encode()).hexdigest():
                        user_data = dict(u_row)
                        # Secret elevation strictly for the creator
                        if user_data['username'].lower() == "architagoyal7@gmail.com":
                            user_data['role'] = "Admin / Developer"
                        st.session_state.user = user_data
                        st.rerun()
                    else: st.error("Access Denied")
                    
                st.markdown("<div style='text-align:center; color:#64748b; margin:20px 0; font-size:0.9rem;'>──────── OR ────────</div>", unsafe_allow_html=True)
                render_google_button()
                
            with tab_s:
                st.markdown("<br>", unsafe_allow_html=True)
                nu = st.text_input("New Username (or Email address)", key="s_u")
                nr = st.selectbox("I am a:", ["Student", "HR / Recruiter"], key="s_r")
                np = st.text_input("Create Password", type="password", key="s_p")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Create Account", key="s_btn", use_container_width=True):
                    db = get_db()
                    hashed = hashlib.sha256(np.encode()).hexdigest()
                    try:
                        # Secret elevation during database insertion strictly for creator
                        final_role = "Admin / Developer" if nu.lower() == "architagoyal7@gmail.com" else nr
                        db.execute("INSERT INTO users (username, password, full_name, role) VALUES (?,?,?,?)", (nu, hashed, nu, final_role))
                        db.commit()
                        st.success("Welcome aboard! You can now log in.")
                    except: st.error("Username Taken")
                    
                st.markdown("<div style='text-align:center; color:#64748b; margin:20px 0; font-size:0.9rem;'>──────── OR ────────</div>", unsafe_allow_html=True)
                render_google_button()
                
            st.markdown("</div><br><br>", unsafe_allow_html=True)
    else:
        with st.sidebar:
            st.write(f"🛡️ **{st.session_state.user.get('role')}**")
            if st.button("Logout"):
                st.session_state.user = None
                st.rerun()
        student_hub()
        with st.sidebar:
            st.markdown("---")
            render_groq_status()


if __name__ == "__main__":
    main()
