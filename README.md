# AI Resume Matcher & Candidate Ranking System

##  Overview

The **AI Resume Matcher & Candidate Ranking System** is an AI-powered web application that helps recruiters quickly evaluate candidates by comparing their resumes with a given Job Description (JD).

The application analyzes the resume and job description using Google's Gemini AI model, calculates a matching score, provides detailed feedback, and ranks multiple candidates based on their scores. This enables recruiters to identify the most suitable candidates without manually reviewing every resume.

---

## Features

* 📄 Upload candidate resumes (PDF)
* 📝 Enter or upload a Job Description
* 🤖 AI-powered resume analysis using Gemini API
* 📊 Resume-JD matching score
* ✅ Skill match analysis
* ❌ Missing skills identification
* 💡 Suggestions for resume improvement
* 🏆 Candidate ranking leaderboard
* 👨‍💼 Recruiter-friendly dashboard
* 🌐 Simple and interactive Streamlit interface

---

## 🛠️ Tech Stack

| Technology          | Purpose                 |
| ------------------- | ----------------------- |
| Python              | Backend Development     |
| Streamlit           | Web Application         |
| Google Gemini API   | AI Resume Analysis      |
| PyPDF2 / PDFPlumber | Resume Text Extraction  |
| Pandas              | Data Processing         |
| NumPy               | Data Handling           |
| SQLite / CSV        | Candidate Score Storage |
| Git & GitHub        | Version Control         |

---

## 📂 Project Structure

```
AI-Resume-Matcher/
│
├── app.py                  # Main Streamlit Application
├── requirements.txt
├── README.md
├── candidates.db           # SQLite database (if used)
├── data/
│   ├── resumes/
│   └── job_descriptions/
├── utils/
│   ├── parser.py
│   ├── gemini.py
│   ├── ranking.py
│   └── database.py
├── assets/
└── screenshots/
```

---

## ⚙️ How It Works

1. Recruiter uploads a candidate's resume.
2. Recruiter enters or uploads the Job Description.
3. Resume text is extracted.
4. Gemini AI analyzes both documents.
5. The application calculates:

   * Overall Match Score
   * Matching Skills
   * Missing Skills
   * Candidate Strengths
   * Areas for Improvement
6. Candidate information is stored.
7. The leaderboard automatically ranks all candidates based on their scores.

---

## 📊 Output

The application provides:

* Overall Match Percentage
* Skill Matching Report
* Missing Skills
* Candidate Strengths
* Resume Improvement Suggestions
* Candidate Ranking Table

Example:

| Rank | Candidate | Match Score |
| ---- | --------- | ----------- |
| 1    | Alice     | 94%         |
| 2    | John      | 90%         |
| 3    | David     | 86%         |
| 4    | Emma      | 81%         |

---

## 💡 Advantages

* Reduces manual resume screening.
* Saves recruiter time.
* Provides objective candidate evaluation.
* Ranks candidates automatically.
* Highlights missing skills instantly.
* Easy-to-use web interface.
* Scalable for multiple candidates.
* AI-generated feedback helps candidates improve resumes.

---

## ⚠️ Limitations

* Matching quality depends on the clarity of the Job Description.
* AI-generated scores should support, not replace, human judgment.
* PDF extraction may not work perfectly for heavily formatted resumes.
* Requires an active internet connection for Gemini API.
* API rate limits may affect large-scale usage.
* Ranking accuracy depends on the quality of extracted resume text.

---

## 📦 Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/AI-Resume-Matcher.git
cd AI-Resume-Matcher
```

### Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Gemini API Key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### Run the Application

```bash
streamlit run app.py
```

---

## 📈 Use Cases

* HR Recruitment
* Campus Placements
* Resume Screening
* Internship Selection
* Hiring Automation
* Talent Acquisition

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Developed by **Sahith Reddy**

If you find this project useful, consider giving it a ⭐ on GitHub.
