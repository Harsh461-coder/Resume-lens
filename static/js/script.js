const fileInput = document.getElementById("resumeFile");
const uploadCard = document.getElementById("uploadCard"); // dropzone div
const fileNote = document.getElementById("fileNote");
const analyzeForm = document.getElementById("analyzeForm");
const analyzeBtn = document.getElementById("analyzeBtn");
const errorNote = document.getElementById("errorNote");
const jobDescription = document.getElementById("jobDescription");

let selectedFile = null;

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
  selectedFile = file;
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
    // keep the real file input in sync so form submission includes it
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

    if (!response.ok) {
      throw new Error("Server returned an error while analyzing.");
    }

    const result = await response.json();

    // stash the result so results.html can read it after redirect
    sessionStorage.setItem("analysisResult", JSON.stringify(result));
    window.location.href = "results.html";
  } catch (err) {
    errorNote.textContent = "Something went wrong. Please try again.";
    console.error(err);
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze my resume";
  }
});

// ---------- Sidebar active state ----------
// Purely visual: highlights whichever sidebar item is clicked.
// Only "Dashboard" actually goes anywhere right now — the rest
// are placeholders until those pages/features are built.
document.querySelectorAll(".side-item").forEach((item) => {
  item.addEventListener("click", (event) => {
    if (item.getAttribute("href") === "#") {
      event.preventDefault();
    }
    document.querySelectorAll(".side-item").forEach((el) => el.classList.remove("active"));
    item.classList.add("active");
  });
});
