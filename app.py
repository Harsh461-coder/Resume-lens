"""
Intelligent ATS Resume Analyzer
BCA Project - Flask backend

Routes:
    GET  /            -> landing page (index.html)
    GET  /analyze      -> upload + job description page (login required)
    POST /analyze        -> runs the analysis pipeline (login required)
    GET  /results          -> results page (reads sessionStorage on the client)
    GET  /dashboard          -> dashboard summary, scoped to the logged-in user
    GET  /history               -> analysis history, scoped to the logged-in user
    GET  /profile                 -> profile page (edit name / change password)
    POST /profile/update-name       -> updates the logged-in user's name
    POST /profile/update-password     -> updates the logged-in user's password
    GET  /api/history              -> past analyses as JSON, scoped to the logged-in user
    GET  /report/<id>                 -> downloads a PDF report (only your own)
    GET  /signin                        -> sign-in page
    POST /signin                          -> verifies credentials, starts a session
    GET  /signup                            -> sign-up page
    POST /signup                              -> creates an account, starts a session
    GET  /logout                                -> clears the session
"""

import os
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify, send_file, abort,
    session, redirect, url_for
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from backend.analyzer.analyzer import analyze_resume
from backend.analyzer.report import generate_report_pdf
from database import (
    init_db, save_analysis, get_history, get_stats, get_analysis_by_id,
    create_user, get_user_by_email, get_user_by_id,
    get_score_trend, get_top_missing_skills, update_user_name, update_user_password,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "development-only-secret")

MAX_FILE_SIZE = 4 * 1024 * 1024  # 4 MB, matches the frontend's limit
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

# Gunicorn (used by Render) imports this module and does not execute the
# development-only block at the bottom of this file.
init_db()
# ---------------------------------------------------------- Auth helpers

def login_required(view):
    """Redirect to /signin (with a ?next= back-link) if nobody's logged in."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("signin", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_current_user():
    """Makes `current_user` available in every template automatically."""
    user_id = session.get("user_id")
    return {"current_user": get_user_by_id(user_id) if user_id else None}


def _score_class(score):
    """Small helper so templates can color-code a score without inline Jinja logic."""
    if score >= 80:
        return "good"
    if score >= 50:
        return "mid"
    return "low"


# --------------------------------------------------------------- Pages

@app.route("/")
def index():
    return render_template("index.html", active_page="home")


@app.route("/analyze")
@login_required
def analyze_page():
    return render_template("analyze.html", active_page="")


@app.route("/results")
@login_required
def results():
    return render_template("results.html", active_page="history")


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    stats = get_stats(user_id)
    recent = get_history(user_id, limit=5)
    for entry in recent:
        entry["score_class"] = _score_class(entry["match_score"])

    score_trend = get_score_trend(user_id, limit=8)
    top_missing_skills = get_top_missing_skills(user_id, limit=5)

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        stats=stats,
        recent=recent,
        score_trend=score_trend,
        top_missing_skills=top_missing_skills,
    )


@app.route("/history")
@login_required
def history():
    user_id = session["user_id"]
    entries = get_history(user_id, limit=50)
    for entry in entries:
        entry["score_class"] = _score_class(entry["match_score"])
    return render_template("history.html", active_page="history", entries=entries)


@app.route("/profile")
@login_required
def profile():
    user_id = session["user_id"]
    stats = get_stats(user_id)
    return render_template("profile.html", active_page="profile", stats=stats)


@app.route("/profile/update-name", methods=["POST"])
@login_required
def profile_update_name():
    full_name = request.form.get("fullname", "").strip()

    if not full_name:
        stats = get_stats(session["user_id"])
        return render_template(
            "profile.html", active_page="profile", stats=stats,
            name_error="Full name cannot be empty.",
        ), 400

    update_user_name(session["user_id"], full_name)
    stats = get_stats(session["user_id"])
    return render_template(
        "profile.html", active_page="profile", stats=stats,
        name_success="Your name has been updated.",
    )


@app.route("/profile/update-password", methods=["POST"])
@login_required
def profile_update_password():
    current_password = request.form.get("currentPassword", "")
    new_password = request.form.get("newPassword", "")
    confirm_password = request.form.get("confirmNewPassword", "")

    user = get_user_by_id(session["user_id"])
    stats = get_stats(session["user_id"])

    if not check_password_hash(user["password_hash"], current_password):
        return render_template(
            "profile.html", active_page="profile", stats=stats,
            password_error="Your current password is incorrect.",
        ), 401

    if new_password != confirm_password:
        return render_template(
            "profile.html", active_page="profile", stats=stats,
            password_error="New passwords do not match.",
        ), 400

    if len(new_password) < 8:
        return render_template(
            "profile.html", active_page="profile", stats=stats,
            password_error="New password must be at least 8 characters.",
        ), 400

    update_user_password(session["user_id"], generate_password_hash(new_password))
    return render_template(
        "profile.html", active_page="profile", stats=stats,
        password_success="Your password has been changed.",
    )


# ---------------------------------------------------------------- Auth

@app.route("/signin", methods=["GET"])
def signin():
    return render_template("signin.html")


@app.route("/signin", methods=["POST"])
def signin_submit():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template(
            "signin.html", error="Incorrect email or password. Please try again."
        ), 401

    session["user_id"] = user["id"]
    next_url = request.args.get("next") or url_for("dashboard")
    return redirect(next_url)


@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")


@app.route("/signup", methods=["POST"])
def signup_submit():
    full_name = request.form.get("fullname", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirmPassword", "")

    if not full_name or not email or not password:
        return render_template("signup.html", error="Please fill in all required fields."), 400

    if password != confirm_password:
        return render_template("signup.html", error="Passwords do not match."), 400

    if len(password) < 8:
        return render_template("signup.html", error="Password must be at least 8 characters."), 400

    if get_user_by_email(email):
        return render_template(
            "signup.html", error="An account with this email already exists. Try signing in instead."
        ), 409

    password_hash = generate_password_hash(password)
    user_id = create_user(full_name, email, password_hash)

    session["user_id"] = user_id
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))


# ------------------------------------------------------------- Analyze

@app.route("/analyze", methods=["POST"])
@login_required
def analyze():
    resume_file = request.files.get("resume")
    job_description = request.form.get("job_description", "").strip()

    if not resume_file or resume_file.filename == "":
        return jsonify({"error": "No resume file uploaded."}), 400

    if not resume_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported."}), 400

    if not job_description:
        return jsonify({"error": "Job description is required."}), 400

    try:
        result = analyze_resume(
            file_stream=resume_file.stream,
            job_description=job_description,
            resume_filename=resume_file.filename,
        )
    except Exception:
        app.logger.exception("Analysis failed")
        return jsonify({"error": "Could not analyze this resume. Please try a different PDF."}), 500

    save_id = save_analysis(result, user_id=session["user_id"])
    result["id"] = save_id
    return jsonify(result)

@app.errorhandler(413)
def file_too_large(_error):
    """Return a clear message if Flask rejects an oversized upload."""
    return jsonify({"error": "The PDF is larger than the 4 MB file limit."}), 413


@app.route("/report/<int:analysis_id>")
@login_required
def download_report(analysis_id):
    entry = get_analysis_by_id(analysis_id, user_id=session["user_id"])
    if entry is None:
        abort(404)

    try:
        filepath = generate_report_pdf(entry)
    except Exception:
        app.logger.exception("Report generation failed")
        abort(500)

    download_name = f"ResumeLens_Report_{entry['resume_filename'].rsplit('.', 1)[0]}.pdf"
    return send_file(filepath, as_attachment=True, download_name=download_name)


@app.route("/api/history")
@login_required
def api_history():
    """JSON API for programmatic access to the logged-in user's history."""
    return jsonify(get_history(session["user_id"]))


if __name__ == "__main__":
    app.run(debug=True)
