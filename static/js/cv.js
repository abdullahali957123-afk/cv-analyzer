const cvSection = document.getElementById("cvSection");
const dropZone = document.getElementById("dropZone");
const cvInput = document.getElementById("cvInput");
const cvMessage = document.getElementById("cvMessage");
const fileInfo = document.getElementById("fileInfo");
const fileName = document.getElementById("fileName");
const fileSize = document.getElementById("fileSize");
const removeFile = document.getElementById("removeFile");
const extractBox = document.getElementById("extractBox");
const extractedText = document.getElementById("extractedText");
const sectionsBox = document.getElementById("sectionsBox");
const missingNote = document.getElementById("missingNote");

const MAX_SIZE = 5 * 1024 * 1024; // 5 MB

// CV section sirf "CV Analyzer" menu par dikhe
document.querySelectorAll(".nav-link").forEach(function (link) {
  link.addEventListener("click", function () {
    if (link.dataset.page === "cv") {
      cvSection.style.display = "block";
      document.getElementById("pageText").textContent =
        "Upload your CV and we will analyze it.";
    } else {
      cvSection.style.display = "none";
    }
  });
});

function showMessage(msg, type) {
  cvMessage.textContent = msg;
  cvMessage.className = "cv-message " + type;
}

function resetResult() {
  fileInfo.style.display = "none";
  extractBox.style.display = "none";
  sectionsBox.style.display = "none";
  extractedText.value = "";
  const rb = document.getElementById("resultBox");
  if (rb) rb.style.display = "none";
}

function fillSections(s) {
  document.getElementById("fName").value = s.name;
  document.getElementById("fEmail").value = s.email;
  document.getElementById("fPhone").value = s.phone;
  document.getElementById("fSkills").value = s.skills.join(", ");
  document.getElementById("fEducation").value = s.education;
  document.getElementById("fExperience").value = s.experience;
  document.getElementById("fProjects").value = s.projects;
  document.getElementById("fCertifications").value = s.certifications;

  if (s.missing.length > 0) {
    missingNote.textContent = "These items were not found in your CV: " + s.missing.join(", ");
    missingNote.className = "missing-note";
  } else {
    missingNote.textContent = "All key sections were found.";
    missingNote.className = "missing-note ok";
  }
  sectionsBox.style.display = "block";
}

async function handleFile(file) {
  const name = file.name.toLowerCase();

  if (!name.endsWith(".pdf") && !name.endsWith(".docx")) {
    showMessage("Only PDF or DOCX files are allowed.", "error");
    resetResult();
    return;
  }

  if (file.size > MAX_SIZE) {
    showMessage("The file is too large. Maximum size is 5 MB.", "error");
    resetResult();
    return;
  }

  fileName.textContent = file.name;
  fileSize.textContent = (file.size / 1024).toFixed(1) + " KB";
  fileInfo.style.display = "block";
  extractBox.style.display = "none";
  sectionsBox.style.display = "none";
  showMessage("Reading your CV, please wait...", "success");

  const formData = new FormData();
  formData.append("cv", file);

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });
    const result = await response.json();

    if (!response.ok) {
      showMessage(result.error || "Something went wrong.", "error");
      extractBox.style.display = "none";
      sectionsBox.style.display = "none";
      return;
    }

    extractedText.value = result.text;
    extractBox.style.display = "block";
    fillSections(result.sections);
    showMessage("CV text extracted successfully.", "success");
  } catch (err) {
    showMessage("Could not reach the server. Is Flask running?", "error");
  }
}

dropZone.addEventListener("click", function () {
  cvInput.click();
});

dropZone.addEventListener("keydown", function (e) {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    cvInput.click();
  }
});

cvInput.addEventListener("change", function () {
  if (cvInput.files.length > 0) {
    handleFile(cvInput.files[0]);
  }
});

dropZone.addEventListener("dragover", function (e) {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", function () {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", function (e) {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files.length > 0) {
    handleFile(e.dataTransfer.files[0]);
  }
});

removeFile.addEventListener("click", function () {
  cvInput.value = "";
  cvMessage.textContent = "";
  resetResult();
});
