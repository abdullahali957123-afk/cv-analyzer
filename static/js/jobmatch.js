const jobSection = document.getElementById("jobSection");
const jobText = document.getElementById("jobText");
const matchBtn = document.getElementById("matchBtn");
const jobMessage = document.getElementById("jobMessage");
const matchResult = document.getElementById("matchResult");

// Show the job section only on the "Job Matcher" menu
document.querySelectorAll(".nav-link").forEach(function (link) {
  link.addEventListener("click", function () {
    if (link.dataset.page === "jobs") {
      jobSection.style.display = "block";
      document.getElementById("pageText").textContent =
        "Paste a job description to see how well your CV matches.";
    } else {
      jobSection.style.display = "none";
    }
  });
});

function jobError(msg) {
  jobMessage.textContent = msg;
  jobMessage.className = "cv-message error";
}

function skillBlock(title, items) {
  if (items.length === 0) return "";
  let html = "<h4>" + esc(title) + "</h4>";
  html += '<div class="chips">';
  items.forEach(function (i) {
    html += '<span class="chip ' + i.status + '">' + esc(i.skill) + "</span>";
  });
  html += "</div><ul class='reason-list'>";
  items.forEach(function (i) {
    html += "<li><strong>" + esc(i.skill) + ":</strong> " + esc(i.reason) + "</li>";
  });
  html += "</ul>";
  return html;
}

function showMatch(r) {
  window.lastMatch = r;
  let html = "<h3>Match Result</h3>";
  html += '<div class="score-big">' + r.overall + "%</div>";

  html += "<h4>How the score was calculated</h4>";
  r.components.forEach(function (c) {
    html += '<div class="cat">';
    html += '<div class="cat-head"><span>' + esc(c.name) + " (weight " + c.weight + "%)</span><span>" + c.points + " points</span></div>";
    html += '<div class="bar"><div class="bar-fill ' + (c.score_pct < 60 ? "low" : "") + '" style="width:' + c.score_pct + '%"></div></div>';
    html += '<p class="cat-why">' + esc(c.detail) + "</p></div>";
  });

  html += skillBlock("Required skills", r.required);
  html += skillBlock("Preferred skills", r.preferred);

  if (r.gaps.length > 0) {
    html += "<h4>Eligibility notes</h4><ul class='reason-list'>";
    r.gaps.forEach(function (g) { html += "<li>" + esc(g) + "</li>"; });
    html += "</ul>";
  }

  html += "<h4>Next steps</h4><ul class='reason-list'>";
  r.next_steps.forEach(function (s) { html += "<li>" + esc(s) + "</li>"; });
  html += "</ul>";

  html += '<div class="result-note">' + esc(r.disclaimer) + "</div>";

  matchResult.innerHTML = html;
  matchResult.style.display = "block";

  document.getElementById("skillGapValue").textContent = r.missing_required_count;
  document.getElementById("skillGapNote").textContent = "Required skills not found in your CV";
}

matchBtn.addEventListener("click", async function () {
  jobMessage.textContent = "";
  matchResult.style.display = "none";

  const cv = collectData();
  if (!cv.skills.trim() && !cv.education.trim() && !cv.projects.trim()) {
    jobError("Please upload your CV in CV Analyzer first.");
    return;
  }
  if (jobText.value.trim().length < 30) {
    jobError("The job description is too short. Please paste the full description.");
    return;
  }

  matchBtn.disabled = true;
  matchBtn.textContent = "Matching...";
  try {
    const response = await fetch("/api/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cv: cv, job: jobText.value }),
    });
    const result = await response.json();
    if (!response.ok) {
      jobError(result.error || "Something went wrong.");
    } else {
      showMatch(result);
    }
  } catch (err) {
    jobError("Could not reach the server. Is Flask running?");
  }
  matchBtn.disabled = false;
  matchBtn.textContent = "Match";
});
