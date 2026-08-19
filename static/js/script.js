// Common JS shared across pages — currently just sidebar placeholder handling.
// Real navigation links (Dashboard, Resumes) work normally; items that don't
// have a page yet (Profile, Analytics, Insights, Settings) stay inert.
document.querySelectorAll(".side-item").forEach((item) => {
  item.addEventListener("click", (event) => {
    if (item.getAttribute("href") === "#") {
      event.preventDefault();
    }
  });
});
