const analyzeBtn = document.getElementById("analyzeBtn");
const resultBox = document.getElementById("resultBox");

function esc(t) {
  const d = document.createElement("div");
  d.textContent = t;
  return d.innerHTML;
}

function collectData() {
  return {
    name: document.getElementById("fName").value,
    email: document.getElementById("fEmail").value,
    phone: document.getElementById("fPhone").value,
    skills: document.getElementById("fSkills").value,
    education: document.getElementById("fEducation").value,
    experience: document.getElementById("fExperience").value,
    projects: document.getElementById("fProjects").value,
    certifications: document.getElementById("fCertifications").value,
  };
}

function showResult(r) {
  let html = "<h3>CV Analysis</h3>";
  html += '<div class="score-big">' + r.total + "/100</div>";
  html += "<p><strong>" + esc(r.label) + "</strong></p>";

  r.categories.forEach(function (c) {
    const pct = Math.round((c.score / c.max) * 100);
    html += '<div class="cat">';
    html += '<div class="cat-head"><span>' + esc(c.name) + "</span><span>" + c.score + "/" + c.max + "</span></div>";
    html += '<div class="bar"><div class="bar-fill ' + (pct < 60 ? "low" : "") + '" style="width:' + pct + '%"></div></div>';
    html += '<p class="cat-msg">' + esc(c.message) + "</p>";
    html += '<p class="cat-why">Why: ' + esc(c.why) + "</p>";
    html += "</div>";
  });

  html += '<div class="result-note"><strong>How to write a bullet point:</strong> ' + esc(r.bullet_tip) + "</div>";
  html += '<div class="result-note">' + esc(r.note) + "</div>";

  resultBox.innerHTML = html;
  resultBox.style.display = "block";

  document.getElementById("cvScoreValue").textContent = r.total + "/100";
  document.getElementById("cvScoreNote").textContent = "Rule-based score from your CV";
}

analyzeBtn.addEventListener("click", async function () {
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(collectData()),
    });
    const result = await response.json();
    if (!response.ok) {
      resultBox.innerHTML = '<p class="cv-message error">' + esc(result.error || "Something went wrong.") + "</p>";
      resultBox.style.display = "block";
    } else {
      showResult(result);
    }
  } catch (err) {
    resultBox.innerHTML = '<p class="cv-message error">Could not reach the server.</p>';
    resultBox.style.display = "block";
  }
  analyzeBtn.disabled = false;
  analyzeBtn.textContent = "Analyze CV";
});
