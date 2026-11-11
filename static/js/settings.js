const settingsSection = document.getElementById("settingsSection");
const profileStatus = document.getElementById("profileStatus");
const profileMessage = document.getElementById("profileMessage");
const historyToggle = document.getElementById("historyToggle");
const historyList = document.getElementById("historyList");
const savedList = document.getElementById("savedList");
const deleteMessage = document.getElementById("deleteMessage");

function setMsg(el, msg, type) {
  el.textContent = msg;
  el.className = "cv-message " + type;
}

async function loadSettings() {
  try {
    const response = await fetch("/api/settings");
    const s = await response.json();

    profileStatus.textContent = s.profile
      ? "A profile is saved" + (s.profile.name ? " for " + s.profile.name : "") + " (updated " + s.profile.updated_at + ")."
      : "No profile is saved.";
    historyToggle.checked = s.save_history;

    if (s.history.length === 0) {
      historyList.innerHTML = '<p class="drop-sub">No history saved.</p>';
    } else {
      let html = "";
      s.history.forEach(function (h) {
        html += '<div class="saved-row"><span>' + esc(h.kind) + " - " + esc(String(h.score)) + "</span><span>" + esc(h.created_at) + "</span></div>";
      });
      historyList.innerHTML = html;
    }

    if (s.saved_jobs.length === 0) {
      savedList.innerHTML = '<p class="drop-sub">No saved jobs. These are sample listings, not real vacancies.</p>';
    } else {
      let html = "";
      s.saved_jobs.forEach(function (j) {
        html += '<div class="saved-row"><span>' + esc(j.title) + " (SAMPLE)</span>" +
          '<button class="remove-saved" data-id="' + esc(j.job_id) + '">Remove</button></div>';
      });
      savedList.innerHTML = html;
    }
  } catch (err) {
    setMsg(profileMessage, "Could not reach the server. Is Flask running?", "error");
  }
}

document.querySelectorAll(".nav-link").forEach(function (link) {
  link.addEventListener("click", function () {
    if (link.dataset.page === "settings") {
      settingsSection.style.display = "block";
      document.getElementById("pageText").textContent = "Manage your saved data and privacy.";
      loadSettings();
    } else {
      settingsSection.style.display = "none";
    }
  });
});

document.getElementById("saveProfileBtn").addEventListener("click", async function () {
  const response = await fetch("/api/profile", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(collectData()),
  });
  const result = await response.json();
  if (response.ok) {
    setMsg(profileMessage, "Profile saved on this computer.", "success");
    loadSettings();
  } else {
    setMsg(profileMessage, result.error || "Something went wrong.", "error");
  }
});

document.getElementById("loadProfileBtn").addEventListener("click", async function () {
  const response = await fetch("/api/profile");
  const result = await response.json();
  if (!response.ok) {
    setMsg(profileMessage, result.error || "No saved profile found.", "error");
    return;
  }
  const d = result.data;
  document.getElementById("fName").value = d.name;
  document.getElementById("fEmail").value = d.email;
  document.getElementById("fPhone").value = d.phone;
  document.getElementById("fSkills").value = d.skills;
  document.getElementById("fEducation").value = d.education;
  document.getElementById("fExperience").value = d.experience;
  document.getElementById("fProjects").value = d.projects;
  document.getElementById("fCertifications").value = d.certifications;
  const note = document.getElementById("missingNote");
  note.textContent = "Loaded from your saved profile.";
  note.className = "missing-note ok";
  document.getElementById("sectionsBox").style.display = "block";
  setMsg(profileMessage, "Saved profile loaded. Open CV Analyzer to see it.", "success");
});

historyToggle.addEventListener("change", async function () {
  await fetch("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ save_history: historyToggle.checked }),
  });
  loadSettings();
});

savedList.addEventListener("click", async function (e) {
  if (!e.target.classList.contains("remove-saved")) return;
  await fetch("/api/saved-jobs/" + encodeURIComponent(e.target.dataset.id), { method: "DELETE" });
  loadSettings();
});

document.getElementById("deleteAllBtn").addEventListener("click", async function () {
  if (!confirm("Delete your saved profile, history, saved jobs and settings? This cannot be undone.")) return;
  const response = await fetch("/api/data", { method: "DELETE" });
  if (response.ok) {
    setMsg(deleteMessage, "All your saved data was deleted.", "success");
    loadSettings();
  } else {
    setMsg(deleteMessage, "Something went wrong.", "error");
  }
});
