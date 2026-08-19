// ---------- Show/hide password toggles ----------
document.querySelectorAll(".su-eye-toggle").forEach((btn) => {
  btn.addEventListener("click", () => {
    const targetId = btn.getAttribute("data-target");
    const input = document.getElementById(targetId);
    const icon = btn.querySelector("i");
    const isHidden = input.type === "password";
    input.type = isHidden ? "text" : "password";
    icon.classList.toggle("fa-eye");
    icon.classList.toggle("fa-eye-slash");
  });
});

// ---------- Password strength meter + live checklist ----------
const passwordInput = document.getElementById("password");
const confirmInput = document.getElementById("confirmPassword");
const matchNote = document.getElementById("matchNote");

const bars = [
  document.getElementById("bar1"),
  document.getElementById("bar2"),
  document.getElementById("bar3"),
  document.getElementById("bar4"),
];
const strengthLabel = document.getElementById("strengthLabel");

const reqLength = document.getElementById("reqLength");
const reqUpper = document.getElementById("reqUpper");
const reqNumber = document.getElementById("reqNumber");

function evaluateStrength(value) {
  const hasLength = value.length >= 8;
  const hasUpper = /[A-Z]/.test(value);
  const hasNumberOrSpecial = /[0-9]|[^A-Za-z0-9]/.test(value);
  const hasLower = /[a-z]/.test(value);

  reqLength.classList.toggle("met", hasLength);
  reqUpper.classList.toggle("met", hasUpper);
  reqNumber.classList.toggle("met", hasNumberOrSpecial);

  let score = 0;
  if (hasLength) score++;
  if (hasUpper) score++;
  if (hasNumberOrSpecial) score++;
  if (hasLower && value.length >= 12) score++;

  bars.forEach((b) => (b.className = ""));

  if (value.length === 0) {
    strengthLabel.textContent = "—";
    strengthLabel.className = "su-strength-label";
    return;
  }

  let tier = "weak";
  let activeBars = 1;

  if (score >= 4) {
    tier = "strong";
    activeBars = 4;
  } else if (score === 3) {
    tier = "strong";
    activeBars = 3;
  } else if (score === 2) {
    tier = "fair";
    activeBars = 2;
  } else {
    tier = "weak";
    activeBars = 1;
  }

  for (let i = 0; i < activeBars; i++) {
    bars[i].classList.add(`on-${tier}`);
  }

  strengthLabel.textContent = tier === "strong" ? "Strong" : tier === "fair" ? "Fair" : "Weak";
  strengthLabel.className = "su-strength-label " + tier;
}

function checkMatch() {
  if (!confirmInput.value) {
    matchNote.textContent = "";
    matchNote.className = "su-match-note";
    confirmInput.classList.remove("valid", "invalid");
    return;
  }
  const matches = passwordInput.value === confirmInput.value;
  matchNote.textContent = matches ? "Passwords match" : "Passwords do not match";
  matchNote.className = "su-match-note " + (matches ? "ok" : "bad");
  confirmInput.classList.toggle("valid", matches);
  confirmInput.classList.toggle("invalid", !matches);
}

passwordInput.addEventListener("input", () => {
  evaluateStrength(passwordInput.value);
  checkMatch();
});
confirmInput.addEventListener("input", checkMatch);

// ---------- "Get started faster" option cards ----------
document.querySelectorAll(".su-option-card").forEach((card) => {
  card.addEventListener("click", () => {
    document.querySelectorAll(".su-option-card").forEach((c) => c.classList.remove("active"));
    card.classList.add("active");
  });
});

// ---------- Form submit ----------
// Client-side validation only blocks submission on real problems;
// otherwise the form submits normally to POST /signup.
const signupForm = document.getElementById("signupForm");
const signupNote = document.getElementById("signupNote");

signupForm.addEventListener("submit", (event) => {
  if (passwordInput.value !== confirmInput.value) {
    event.preventDefault();
    signupNote.textContent = "Please make sure your passwords match before continuing.";
    confirmInput.focus();
    return;
  }

  if (passwordInput.value.length < 8) {
    event.preventDefault();
    signupNote.textContent = "Password must be at least 8 characters.";
    passwordInput.focus();
    return;
  }
  // Otherwise let the browser submit the form normally.
});
