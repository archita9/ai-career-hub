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
from resume_parser import parse_resume

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
    is_dark = st.session_state.theme == 'dark'
    bg, card, text = ("#0f172a", "#1e293b", "#e2e8f0") if is_dark else ("#f1f5f9", "#ffffff", "#0f172a")
    st.markdown(f"<style>.stApp{{background-color:{bg}; color:{text};}} .main-card{{background:{card}; padding:20px; border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.2); margin-bottom:20px; color:{text};}}</style>", unsafe_allow_html=True)
    st.markdown("<div style='position:fixed; top:15px; right:20px; font-size:40px; z-index:1000;'>🐼</div>", unsafe_allow_html=True)

apply_theme()

# =========================
# DB
# =========================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

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
    st.write("The 'Plus Factors' that college didn't teach you.")
    
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
    st.write("### 💡 What Research Colleges won't tell you:")
    st.info("Directly 'Calling HR' or cold-emailing with your ATS score is a major 'Plus' over 90% of applicants who just 'Easy Apply'. Deep research on company products wins interviews.")

# =========================
# GAME ZONE
# =========================
def game_zone():
    st.markdown("## 🎮 Skill Gaming & Streaks")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.subheader("🔥 Daily Placement Streak")
        itms = ["Apply to job", "Cold email HR", "Study Theory", "Project work", "Git commit", "LinkedIn post", "Email reading", "Company Search", "Mock Test", "DSA Solve", "Portfolio fix", "Networking"]
        done = 0
        for i, itm in enumerate(itms):
            if st.checkbox(itm, key=f"streak_{i}"): done += 1
        st.progress(done / len(itms))
        st.write(f"Status: **{done} / {len(itms)}** streak complete")
        if done >= len(itms): 
            st.markdown("<h2 style='text-align:center;'>🏆 Trophy Unlocked!</h2>", unsafe_allow_html=True)
            st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.subheader("👑 4-Queens Mind Game")
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
    st.markdown("# 🎓 AI Career Hub")
    tabs = st.tabs(["📊 Analysis", "✨ Dream Quest", "🛣️ Roadmap", "🏆 Contests", "💼 Internships", "🚀 Launchpad", "🎮 Game Zone", "🎙️ AI Room"])
    
    with tabs[0]: # Analysis
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("<div class='main-card'>", unsafe_allow_html=True)
            st.subheader("📄 Phase 1: AI Analysis")
            uploaded = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="analysis_up")
            if uploaded:
                st.session_state.resume_data = parse_resume(uploaded)
                data = st.session_state.resume_data
                st.success("Analysis Complete!")
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

    with tabs[1]: dream_quest()
    
    with tabs[2]: # Roadmap
        role = st.selectbox("Select Pathway Filter:", list(ROLE_INFO.keys()), key="rm_sel_hub")
        st.markdown(f"## 🛣️ {role} Pathway")
        st.write("### 📚 Recommended Courses (Free & Paid)")
        for crs in ROLE_INFO[role]['courses']:
            st.markdown(f"<div class='main-card'><b>{crs['name']}</b> ({crs['platform']}) - <i>{crs['type']}</i></div>", unsafe_allow_html=True)
        
        rm = ROLE_INFO[role]['roadmap']
        cc1, cc2, cc3 = st.columns(3)
        for i, level in enumerate(["Beginner", "Intermediate", "Advanced"]):
            with [cc1, cc2, cc3][i]:
                st.markdown(f"<div class='main-card'>", unsafe_allow_html=True)
                st.subheader(level)
                for t in rm[level]['topics']: st.write(f"• {t}")
                st.success(f"🚀 {rm[level]['project']}")
                st.markdown("</div>", unsafe_allow_html=True)

    with tabs[3]: # Contests
        for cat, items in LIVE_CONTESTS.items():
            st.subheader(cat)
            for itm in items:
                st.markdown(f"<div class='main-card'><b>{itm['name']}</b><br>Plus Overview: {itm['plus']}<br>Prizes: {itm['reward']} | Mode: {itm['mode']}</div>", unsafe_allow_html=True)

    with tabs[4]: # Internships
        st.markdown("## 💼 Internship opportunities")
        f = st.radio("Field Filter:", ["All"] + list(ROLE_INFO.keys()), horizontal=True)
        disp = [i for i in INTERNSHIPS if f == "All" or i['field'] == f]
        st.map(pd.DataFrame(disp))
        for i in disp: st.markdown(f"<div class='main-card'>{i['role']} @ {i['name']} ({i['city']})</div>", unsafe_allow_html=True)

    with tabs[5]: launchpad_pro(st.session_state.resume_data.get('detected_domain', 'Software Developer') if st.session_state.resume_data else "Software Developer")
    with tabs[6]: game_zone()

    with tabs[7]: # AI Room & Subscription
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
                        # AI Response
                        resp = f"Panda Copilot: That's a great question about '{prompt}'. To reach your dream role, you should focus on the 'Plus Factors' mentioned in your Dream Quest tab. Specifically, the projects in the Roadmap will give you the edge."
                        st.session_state.messages.append({"role": "assistant", "content": resp})
                        with st.chat_message("assistant"): st.markdown(resp)
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

# =========================
# MAIN
# =========================
def main():
    if not st.session_state.user:
        st.markdown("<h1 style='text-align: center; color:#38bdf8;'>🐼 Placement Pro AI</h1>", unsafe_allow_html=True)
        tab_l, tab_s = st.tabs(["Login", "Sign Up"])
        with tab_l:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("Login", key="l_btn"):
                db = get_db()
                u_row = db.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
                if u_row and u_row['password'] == hashlib.sha256(p.encode()).hexdigest():
                    st.session_state.user = dict(u_row)
                    st.rerun()
                else: st.error("Access Denied")
        with tab_s:
            nu = st.text_input("New ID", key="s_u")
            nr = st.selectbox("I am a:", ["Student", "HR / Recruiter"], key="s_r")
            np = st.text_input("Password", type="password", key="s_p")
            if st.button("Register", key="s_btn"):
                db = get_db()
                hashed = hashlib.sha256(np.encode()).hexdigest()
                try:
                    db.execute("INSERT INTO users (username, password, full_name, role) VALUES (?,?,?,?)", (nu, hashed, nu, nr))
                    db.commit()
                    st.success("Welcome aboard!")
                except: st.error("ID Taken")
    else:
        with st.sidebar:
            st.write(f"🛡️ **{st.session_state.user.get('role')}**")
            if st.button("Logout"):
                st.session_state.user = None
                st.rerun()
        student_hub()

if __name__ == "__main__":
    main()
