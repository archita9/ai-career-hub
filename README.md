# 🐼 AI Career & Talent Hub (V12.0)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-career-hub.streamlit.app/)
[![GitHub license](https://img.shields.io/github/license/archita9/ai-career-hub)](https://github.com/archita9/ai-career-hub/blob/main/LICENSE)

An industry-grade, gamified AI ecosystem designed to guide students and freshers from initial resume analysis to landing roles at top-tier companies. This platform combines ML-based placement prediction, NLP-driven resume parsing, and interactive career tools.

---

### 🚀 Key Features

#### 1. 📊 AI-Powered Career Analysis
*   **Precision Resume Parser**: NLP-based skill extraction with Regex word boundaries for 99.9% accuracy.
*   **ATS Matching**: Instantly calculates your ATS score and identifies skill gaps for your target role.
*   **Placement Predictor**: Uses a Scikit-Learn ML model (`placement_model.pkl`) to predict your hiring probability.
*   **Portfolio Health**: Evaluates your GitHub and LinkedIn profile strength.

#### 2. ✨ Phase 2: The Dream Quest
*   **Target Goal Setting**: Define your Dream Company (e.g. Google, NVIDIA) and target role.
*   **Achievement Delta**: Unlocks a specific, high-level "Plus Factor" strategy to bridge the gap between your current state and elite-level positions.

#### 3. 🛣️ Integrated Career Pathway
*   **Multi-Domain Roadmaps**: Tailored learning paths for **Machine Learning, Data Science, Web Development, and Software Developer**.
*   **Curated Learning**: Links to top Free & Paid certifications (Andrew Ng, CS50, Fast.ai, etc.).
*   **Mastery Launchpad**: A "fresher's guide" to DSA, GitHub Commit streaks, and LinkedIn Branding.

#### 4. 🔥 Gamification & Productivity
*   **12-Item Placement Streak**: Daily habit tracker covering cold-emails, GitHub commits, projects, and theory.
*   **👑 Mind Game (4-Queens)**: A problem-solving puzzle to sharpen your mental logic with celebratory award animations.
*   **🏆 Trophy System**: Visual balloons and trophies for milestone achievements.

#### 5. 🌍 Opportunity Map & Live Contests
*   **Hiring Hubs Map**: Interactive map showing Indian tech hubs and live internship locations.
*   **Contest Tracker**: Real-time monitoring of Hackathons (SIH, GRID), Kaggle, and Unstop competitions.
*   **Field Filtering**: Instantly filter map results for ML, Web Dev, or DS roles.

#### 6. 🎙️ AI Copilot & Mentorship
*   **Real-Time Chatbot**: 1:1 conversation with the "Panda AI" for career advice via `st.chat_input`.
*   **Subscription Tiers**: Integrated UPI-ready UI for booking sessions with Industry Mentors (₹499) or HR Professionals (₹999).

---

### 🛠️ Tech Stack & Architecture

*   **Frontend/UI**: [Streamlit](https://streamlit.io/) (High-performance Data App framework)
*   **Backend**: Python, SQL (SQLite3)
*   **Machine Learning**: `scikit-learn`, `pandas`, `numpy`, `pickle`
*   **NLP/Parsing**: `PyPDF2`, `re` (Regex)
*   **Database**: `sqlite3` for user management and career progress tracking
*   **Design**: Vanilla CSS with dark/light theme support and dynamic gradients

---

### ⚙️ Installation & Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/archita9/ai-career-hub.git
    cd ai-career-hub
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize the Database**:
    ```bash
    python init_db.py
    ```

4.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

---

### 🛡️ Pre-launch Checklist
*   [x] Precision Skill Extraction (V12.0 Fix)
*   [x] 20+ Live Internship Entries
*   [x] Automatic Streak Reset Logic
*   [x] AI Chatbot Session Timer
*   [x] 4-Queens Victory Celebration

### 🔗 Connect with me
- **GitHub**: [archita9](https://github.com/archita9)
- **Project Link**: [ai-career-hub](https://github.com/archita9/ai-career-hub)

---

### ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.分析
