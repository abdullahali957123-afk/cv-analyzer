const recommendSection = document.getElementById("recommendSection");
const recBtn = document.getElementById("recBtn");
const recMessage = document.getElementById("recMessage");
const recResults = document.getElementById("recResults");
let optionsLoaded = false;

function recError(msg) {
  recMessage.textContent = msg;
  recMessage.className = "cv-message error";
}

function addChecks(containerId, values) {
  const box = document.getElementById(containerId);
  box.innerHTML = "";
  values.forEach(function (v) {
    const label = document.createElement("label");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.value = v;
    label.appendChild(input);
    label.appendChild(document.createTextNode(" " + v));
    box.appendChild(label);
  });
}

async function loadOptions() {
  if (optionsLoaded) return;
  try {
    const response = await fetch("/api/recommend/options");
    const data = await response.json();
    addChecks("catOptions", data.categories);
    addChecks("typeOptions", data.types);
    optionsLoaded = true;
  } catch (err) {
    recError("Could not load the options. Is Flask running?");
  }
}

function checked(containerId) {
  return Array.from(document.querySelectorAll("#" + containerId + " input:checked")).map(function (i) { return i.value; });
}

document.querySelectorAll(".nav-link").forEach(function (link) {
  link.addEventListener("click", function () {
    if (link.dataset.page === "recommend") {
      recommendSection.style.display = "block";
      document.getElementById("pageText").textContent =
        "Sample jobs ranked by how well they match your CV and preferences.";
      loadOptions();
    } else {
      recommendSection.style.display = "none";
    }
  });
});

function chips(items) {
  let html = '<div class="chips">';
  items.forEach(function (i) {
    html += '<span class="chip ' + i.status + '">' + esc(i.skill) + "</span>";
  });
  return html + "</div>";
}

function renderJobs(data) {
  let html = '<div class="rm-info"><strong>Recommended sample jobs</strong><p>' + esc(data.ranking_note) + "</p></div>";
  data.jobs.forEach(function (j, idx) {
    html += '<div class="rm-card">';
    html += "<h4>#" + (idx + 1) + " " + esc(j.title) + '<span class="badge-sample">' + esc(j.label) + "</span></h4>";
    html += '<p class="job-meta">' + esc(j.company) + " | " + esc(j.category) + " | " + esc(j.type) + " | " + esc(j.location) + "</p>";
    html += "<p>" + esc(j.summary) + "</p>";
    html += '<div class="score-big">' + j.overall + "% match</div>";

    let rank = "Ranking score " + j.rank_score + " = match " + j.overall + "%";
    if (j.category_bonus) rank += " + " + j.category_bonus + " (your preferred category)";
    if (j.type_bonus) rank += " + " + j.type_bonus + " (your preferred job type)";
    html += '<p class="rank-line">' + esc(rank) + "</p>";

    html += "<p><span class='rm-tag'>Required skills:</span></p>" + chips(j.required);
    if (j.preferred.length) html += "<p><span class='rm-tag'>Preferred skills:</span></p>" + chips(j.preferred);

    html += "<details class='q-card-details'><summary>How this match was calculated</summary><ul class='reason-list'>";
    j.components.forEach(function (c) {
      html += "<li>" + esc(c.name) + " (weight " + c.weight + "%): " + esc(c.detail) + " - " + c.points + " points</li>";
    });
    html += "</ul></details>";

    if (j.gaps.length) {
      html += "<p><span class='rm-tag'>Eligibility notes:</span></p><ul class='reason-list'>";
      j.gaps.forEach(function (g) { html += "<li>" + esc(g) + "</li>"; });
      html += "</ul>";
    }
    html += '<button class="save-job-btn" data-id="' + esc(j.id) + '">Save job</button>';
    html += "</div>";
  });
  html += '<div class="result-note">' + esc(data.disclaimer) + "</div>";
  recResults.innerHTML = html;

  const good = data.jobs.filter(function (j) { return j.overall >= 50; }).length;
  document.getElementById("jobMatchesValue").textContent = good;
  document.getElementById("jobMatchesNote").textContent = "Sample jobs with a 50%+ match";
}

recBtn.addEventListener("click", async function () {
  recMessage.textContent = "";
  const cv = collectData();
  if (!cv.skills.trim() && !cv.education.trim() && !cv.projects.trim()) {
    recError("Please upload your CV in CV Analyzer first.");
    return;
  }
  recBtn.disabled = true;
  recBtn.textContent = "Finding matches...";
  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cv: cv, categories: checked("catOptions"), types: checked("typeOptions") }),
    });
    const result = await response.json();
    if (!response.ok) {
      recError(result.error || "Something went wrong.");
    } else {
      renderJobs(result);
    }
  } catch (err) {
    recError("Could not reach the server. Is Flask running?");
  }
  recBtn.disabled = false;
  recBtn.textContent = "Find matches";
});

recResults.addEventListener("click", async function (e) {
  if (!e.target.classList.contains("save-job-btn")) return;
  try {
    const response = await fetch("/api/saved-jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ job_id: e.target.dataset.id }),
    });
    e.target.textContent = response.ok ? "Saved" : "Could not save";
  } catch (err) {
    e.target.textContent = "Could not save";
  }
});
