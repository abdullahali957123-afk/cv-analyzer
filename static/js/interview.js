const interviewSection = document.getElementById("interviewSection");
const genBtn = document.getElementById("genBtn");
const interviewMessage = document.getElementById("interviewMessage");
const questionsBox = document.getElementById("questionsBox");

const practiceScores = [];

// Show the interview section only on the "Interview Prep" menu
document.querySelectorAll(".nav-link").forEach(function (link) {
  link.addEventListener("click", function () {
    if (link.dataset.page === "interview") {
      interviewSection.style.display = "block";
      document.getElementById("pageText").textContent =
        "Practice interview questions based on your CV and job description.";
    } else {
      interviewSection.style.display = "none";
    }
  });
});

function intError(msg) {
  interviewMessage.textContent = msg;
  interviewMessage.className = "cv-message error";
}

function makeCard(q) {
  const card = document.createElement("div");
  card.className = "q-card";
  card.dataset.type = q.type;

  const text = document.createElement("p");
  text.className = "q-text";
  text.textContent = q.question;
  card.appendChild(text);

  const details = document.createElement("details");
  const summary = document.createElement("summary");
  summary.textContent = "Answer guide";
  const guide = document.createElement("p");
  guide.textContent = q.guide;
  details.appendChild(summary);
  details.appendChild(guide);
  card.appendChild(details);

  const area = document.createElement("textarea");
  area.rows = 5;
  area.placeholder = "Type your answer here...";
  area.setAttribute("aria-label", "Your answer");
  card.appendChild(area);

  const btn = document.createElement("button");
  btn.className = "fb-btn";
  btn.textContent = "Get feedback";
  card.appendChild(btn);

  const fb = document.createElement("div");
  fb.className = "fb-box";
  card.appendChild(fb);
  return card;
}

function renderGroup(title, items) {
  if (items.length === 0) return null;
  const group = document.createElement("div");
  group.className = "q-group";
  const h = document.createElement("h3");
  h.textContent = title;
  group.appendChild(h);
  items.forEach(function (q) { group.appendChild(makeCard(q)); });
  return group;
}

function renderQuestions(data) {
  questionsBox.innerHTML = "";
  data.notes.forEach(function (n) {
    const p = document.createElement("div");
    p.className = "result-note";
    p.textContent = n;
    questionsBox.appendChild(p);
  });
  [["Technical questions", data.technical],
   ["Behavioral questions", data.behavioral],
   ["HR questions", data.hr]].forEach(function (g) {
    const el = renderGroup(g[0], g[1]);
    if (el) questionsBox.appendChild(el);
  });
}

genBtn.addEventListener("click", async function () {
  interviewMessage.textContent = "";
  const cv = collectData();
  if (!cv.skills.trim() && !cv.education.trim() && !cv.projects.trim()) {
    intError("Please upload your CV in CV Analyzer first.");
    return;
  }
  genBtn.disabled = true;
  genBtn.textContent = "Generating...";
  try {
    const response = await fetch("/api/interview/questions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cv: cv, job: document.getElementById("jobText").value }),
    });
    const result = await response.json();
    if (!response.ok) {
      intError(result.error || "Something went wrong.");
    } else {
      renderQuestions(result);
    }
  } catch (err) {
    intError("Could not reach the server. Is Flask running?");
  }
  genBtn.disabled = false;
  genBtn.textContent = "Generate questions";
});

function showFeedback(box, r) {
  let html = "<strong>Score: " + r.score + "%</strong> - " + esc(r.summary) + "<ul>";
  r.checks.forEach(function (c) {
    html += '<li class="' + (c.passed ? "check-pass" : "check-fail") + '">' +
      (c.passed ? "Done: " : "Improve: ") + esc(c.label) +
      (c.tip ? " - " + esc(c.tip) : "") + "</li>";
  });
  r.extra.forEach(function (e) { html += "<li>" + esc(e) + "</li>"; });
  html += "</ul>";
  html += '<div class="result-note">' + esc(r.note) + "</div>";
  box.innerHTML = html;
}

questionsBox.addEventListener("click", async function (e) {
  if (!e.target.classList.contains("fb-btn")) return;
  const card = e.target.closest(".q-card");
  const answer = card.querySelector("textarea").value;
  const box = card.querySelector(".fb-box");
  if (answer.trim().length < 5) {
    box.innerHTML = '<span class="check-fail">Please write an answer first.</span>';
    return;
  }
  e.target.disabled = true;
  try {
    const response = await fetch("/api/interview/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: card.dataset.type, answer: answer }),
    });
    const result = await response.json();
    if (!response.ok) {
      box.innerHTML = '<span class="check-fail">' + esc(result.error || "Something went wrong.") + "</span>";
    } else {
      showFeedback(box, result);
      practiceScores.push(result.score);
      const avg = Math.round(practiceScores.reduce(function (a, b) { return a + b; }, 0) / practiceScores.length);
      document.getElementById("readinessValue").textContent = avg + "%";
      document.getElementById("readinessNote").textContent =
        "Average of " + practiceScores.length + " practice answer(s)";
    }
  } catch (err) {
    box.innerHTML = '<span class="check-fail">Could not reach the server.</span>';
  }
  e.target.disabled = false;
});
