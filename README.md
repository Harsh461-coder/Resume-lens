# Intelligent ATS Resume Analyzer

A BCA final year project prototype that helps job applicants check how well their
resume matches a job description before they apply.

> This is a first-version college prototype, not a commercial product. It is
> built only for applicants — not recruiters — and is meant to be extended
> with more features in the future.

## What it does

- Upload your resume (PDF)
- Paste the job description you're applying for
- Get an ATS-style match score
- See which skills from the job description are already in your resume
- See which skills seem to be missing
- Get a few simple suggestions to improve your resume for that job

## Tech stack

- **Frontend:** HTML, CSS, JavaScript (no framework)
- **Backend:** Python, Flask
- **PDF text extraction:** pdfplumber
- **Matching/scoring:** scikit-learn (TF-IDF + cosine similarity), keyword matching against a skills dataset
- **Database:** SQLite (logs each analysis)

## Project structure

```
resumelens/
├── app.py                # Flask routes
├── analyzer.py            # PDF extraction + matching + scoring logic
├── database.py             # SQLite setup and logging
├── requirements.txt
├── data/
│   └── skills.json          # skills dataset used for matching
├── templates/
│   ├── index.html            # upload page
│   └── results.html           # results page
├── static/
│   ├── css/styles.css
│   └── js/
│       ├── script.js          # upload page logic
│       └── results.js          # results page logic
└── uploads/                    # temporary resume storage (gitignored)
```

## Setup and running locally

1. Clone the repository
   ```
   git clone https://github.com/<your-username>/resumelens.git
   cd resumelens
   ```

2. Create a virtual environment (recommended)
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Run the app
   ```
   python app.py
   ```

5. Open your browser at `http://127.0.0.1:5000`

## Deploying on Render

1. Push this `resumelens` folder to a GitHub repository.
2. In Render, create a **Web Service** and connect that repository.
3. Render will use the included `Procfile`. Set the build command to
   `pip install -r requirements.txt` if Render does not detect it automatically.
4. Add a `FLASK_SECRET_KEY` environment variable. Use a long random value,
   not the sample value in `.env.example`.
5. For a prototype, SQLite will work. Its data is reset after a Render restart
   unless you attach a persistent disk. Mount the disk at `/opt/render/project/src/database`
   to keep accounts and analysis history

## How the matching works

1. Text is extracted from the uploaded resume PDF using `pdfplumber`.
2. Both the resume text and job description are checked against a dataset of
   common skills (`data/skills.json`) to find which skills appear in each.
3. Skills present in both are shown as "matching skills"; skills present in
   the job description but not the resume are shown as "missing skills."
4. An overall match score is calculated using TF-IDF vectors of the full
   resume and job description text, compared with cosine similarity.
5. A few rule-based suggestions are generated based on the missing skills and
   overall score.

## Future scope

- Support uploading and comparing multiple resumes at once
- Rank multiple resumes against the same job description
- Downloadable PDF report of the analysis
- More advanced matching using NLP models

## Author

Harsh Saini
BCA, Panipat Institute of Engineering & Technology (2024–2027)
