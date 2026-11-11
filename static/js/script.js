const links = document.querySelectorAll(".nav-link");
const title = document.getElementById("pageTitle");
const text = document.getElementById("pageText");
const cards = document.getElementById("dashboardCards");
const guide = document.getElementById("dashboardGuide");

links.forEach(function (link) {
  link.addEventListener("click", function (event) {
    event.preventDefault();

    links.forEach(function (l) {
      l.classList.remove("active");
    });
    link.classList.add("active");

    title.textContent = link.textContent;

    if (link.dataset.page === "dashboard") {
      text.textContent = "Welcome, Zainab! Your CV summary will appear here.";
      cards.style.display = "grid";
      guide.style.display = "block";
    } else {
      text.textContent = link.textContent + " page is coming soon.";
      cards.style.display = "none";
      guide.style.display = "none";
    }
  });
});

// Clicking the logo opens the Dashboard
document.querySelector(".brand").addEventListener("click", function (event) {
  event.preventDefault();
  document.querySelector('.nav-link[data-page="dashboard"]').click();
});
