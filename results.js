const dashboard = document.getElementById("dashboard");
const loadingNote = document.getElementById("loadingNote");
const resumeName = document.getElementById("resumeName");
const scoreValue = document.getElementById("scoreValue");
const scoreMessage = document.getElementById("scoreMessage");
const matchedSkillsEl = document.getElementById("matchedSkills");
const missingSkillsEl = document.getElementById("missingSkills");
const suggestionsList = document.getElementById("suggestionsList");

function scoreMessageFor(score) {
  if (score >= 80) return "Great match — you're nearly there!";
  if (score >= 50) return "Decent match — a few gaps to close.";
  return "Low match — consider revising your resume for this role.";
}

function renderResult(result) {
  resumeName.textContent = result.resume_filename || "Your Resume";
  scoreValue.textContent = Math.round(result.match_score);
  scoreMessage.textContent = scoreMessageFor(result.match_score);

  matchedSkillsEl.innerHTML = "";
  (result.matched_skills || []).forEach((skill) => {
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = skill;
    matchedSkillsEl.appendChild(tag);
  });
  if ((result.matched_skills || []).length === 0) {
    matchedSkillsEl.innerHTML = '<span class="tag">No matching skills found</span>';
  }

  missingSkillsEl.innerHTML = "";
  (result.missing_skills || []).forEach((skill) => {
    const tag = document.createElement("span");
    tag.className = "tag missing";
    tag.textContent = skill;
    missingSkillsEl.appendChild(tag);
  });
  if ((result.missing_skills || []).length === 0) {
    missingSkillsEl.innerHTML = '<span class="tag">No obvious gaps found</span>';
  }

  suggestionsList.innerHTML = "";
  (result.suggestions || []).forEach((suggestion) => {
    const li = document.createElement("li");
    li.textContent = suggestion;
    suggestionsList.appendChild(li);
  });

  loadingNote.style.display = "none";
  dashboard.classList.add("visible");
}

const stored = sessionStorage.getItem("analysisResult");

if (stored) {
  try {
    renderResult(JSON.parse(stored));
  } catch (err) {
    loadingNote.textContent = "Couldn't load your results. Please analyze your resume again.";
  }
} else {
  loadingNote.textContent = "No analysis found. Please upload a resume first.";
}
