const roadmapSection = document.getElementById("roadmapSection");
const roadmapContent = document.getElementById("roadmapContent");

function infoBox(msg) {
  roadmapContent.innerHTML = '<div class="rm-info"><p>' + esc(msg) + "</p></div>";
}

function renderRoadmap(r) {
  if (r.items.length === 0) {
    infoBox("No major skill gaps were found for this job. Great work!");
    return;
  }

  let html = '<div class="rm-info"><strong>Your Skills Roadmap</strong><p>Learn from top to bottom: the most important skills come first.</p></div>';
  const groups = [
    ["high", "High priority"],
    ["medium", "Medium priority"],
    ["low", "Low priority"],
  ];
  let n = 0;

  groups.forEach(function (g) {
    const items = r.items.filter(function (i) { return i.priority === g[0]; });
    if (items.length === 0) return;
    html += '<div class="rm-group ' + g[0] + '"><h3>' + g[1] + "</h3>";
    items.forEach(function (i) {
      n += 1;
      html += '<div class="rm-card"><h4>Step ' + n + ": " + esc(i.skill) + "</h4>";
      html += '<p class="cat-why">' + esc(i.reason) + "</p>";
      html += "<p><span class='rm-tag'>Why it matters:</span> " + esc(i.why) + "</p>";
      html += "<p><span class='rm-tag'>Learning steps:</span></p><ol>";
      i.steps.forEach(function (s) { html += "<li>" + esc(s) + "</li>"; });
      html += "</ol>";
      html += "<p><span class='rm-tag'>Practice project:</span> " + esc(i.project) + "</p>";
      html += "<p><span class='rm-tag'>For your portfolio:</span> " + esc(i.portfolio) + "</p>";
      html += "<p><span class='rm-tag'>Resources (search by name):</span> " + esc(i.resources.join(", ")) + "</p>";
      html += "<p><span class='rm-tag'>Estimated time:</span> " + esc(i.time) + "</p>";
      html += "</div>";
    });
    html += "</div>";
  });

  html += '<div class="result-note">' + esc(r.note) + "</div>";
  roadmapContent.innerHTML = html;
}

async function loadRoadmap() {
  if (!window.lastMatch) {
    infoBox("First paste a job description in Job Matcher and click Match. Your roadmap will then appear here.");
    return;
  }
  infoBox("Building your roadmap...");
  try {
    const response = await fetch("/api/roadmap", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        required: window.lastMatch.required,
        preferred: window.lastMatch.preferred,
      }),
    });
    const result = await response.json();
    if (!response.ok) {
      infoBox(result.error || "Something went wrong.");
    } else {
      renderRoadmap(result);
    }
  } catch (err) {
    infoBox("Could not reach the server. Is Flask running?");
  }
}

document.querySelectorAll(".nav-link").forEach(function (link) {
  link.addEventListener("click", function () {
    if (link.dataset.page === "roadmap") {
      roadmapSection.style.display = "block";
      document.getElementById("pageText").textContent =
        "A path to learn the skills missing for your target job.";
      loadRoadmap();
    } else {
      roadmapSection.style.display = "none";
    }
  });
});
