// Upload logic for the /analyze page: drag-drop, file validation,
// and submitting the resume + job description to the backend.

const fileInput = document.getElementById("resumeFile");
const uploadCard = document.getElementById("uploadCard"); // dropzone div
const fileNote = document.getElementById("fileNote");
const analyzeForm = document.getElementById("analyzeForm");
const analyzeBtn = document.getElementById("analyzeBtn");
const errorNote = document.getElementById("errorNote");
const jobDescription = document.getElementById("jobDescription");

function validateFile(file) {
  if (!file) return false;

  if (!file.name.toLowerCase().endsWith(".pdf")) {
    fileNote.textContent = "Please upload a PDF file only.";
    return false;
  }

  if (file.size > 4 * 1024 * 1024) {
    fileNote.textContent = "This file is larger than 4 MB.";
    return false;
  }

  fileNote.textContent = "Ready to analyze: " + file.name;
  return true;
}

fileInput.addEventListener("change", () => {
  validateFile(fileInput.files[0]);
});

["dragenter", "dragover"].forEach((eventName) => {
  uploadCard.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadCard.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  uploadCard.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadCard.classList.remove("dragging");
  });
});

uploadCard.addEventListener("drop", (event) => {
  const file = event.dataTransfer.files[0];
  if (file && validateFile(file)) {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;
  }
});

analyzeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorNote.textContent = "";

  const file = fileInput.files[0];
  const jdText = jobDescription.value.trim();

  if (!file) {
    errorNote.textContent = "Please choose a resume PDF first.";
    return;
  }
  if (!validateFile(file)) {
    return;
  }
  if (!jdText) {
    errorNote.textContent = "Please paste a job description.";
    return;
  }

  const formData = new FormData();
  formData.append("resume", file);
  formData.append("job_description", jdText);

  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(playload.error || "Server returned an error while analyzing.");
    }

    const result = payload;

    sessionStorage.setItem("analysisResult", JSON.stringify(result));
    window.location.href = "/results";
  } catch (err) {
    errorNote.textContent = err.message || "Something went wrong. Please try again.";
    console.error(err);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze my resume";
  }
});
