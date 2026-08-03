// SELECTORS
const categories = document.querySelectorAll(".faq-categories button");
const groups = document.querySelectorAll(".faq-group");
const items = document.querySelectorAll(".faq-item");
const search = document.getElementById("searchInput");
const noResult = document.getElementById("noResult");

// ================= CATEGORY SWITCH (WITH ANIMATION) =================
categories.forEach((btn) => {
  btn.addEventListener("click", (e) => {
    // active button
    categories.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");

    // ripple effect
    let circle = document.createElement("span");
    circle.classList.add("ripple");

    let rect = btn.getBoundingClientRect();
    circle.style.left = e.clientX - rect.left + "px";
    circle.style.top = e.clientY - rect.top + "px";

    btn.appendChild(circle);
    setTimeout(() => circle.remove(), 600);

    // animate groups
    groups.forEach((g) => {
      g.style.opacity = "0";
      g.style.transform = "translateY(20px)";
      g.classList.remove("active");
    });

    setTimeout(() => {
      groups.forEach((g) => {
        if (g.dataset.cat === btn.dataset.cat) {
          g.classList.add("active");

          setTimeout(() => {
            g.style.opacity = "1";
            g.style.transform = "translateY(0)";
          }, 50);
        }
      });
    }, 200);
  });
});

// ================= ACCORDION =================
items.forEach((item) => {
  const q = item.querySelector(".faq-q");

  q.addEventListener("click", () => {
    item.classList.toggle("active");
  });
});

// ================= AUTO OPEN FIRST =================
window.addEventListener("load", () => {
  document.querySelector(".faq-item")?.classList.add("active");
});

search.addEventListener("input", () => {
  let val = search.value.trim().toLowerCase();
  let found = false;

  items.forEach((item) => {
    const q = item.querySelector(".faq-q");
    const a = item.querySelector(".faq-a");

    // REMOVE OLD MARKS ONLY (IMPORTANT)
    q.innerHTML = q.innerHTML.replace(/<mark>|<\/mark>/gi, "");
    a.innerHTML = a.innerHTML.replace(/<mark>|<\/mark>/gi, "");

    const qText = q.textContent.toLowerCase();
    const aText = a.textContent.toLowerCase();

    if ((qText + aText).includes(val)) {
      item.style.display = "block";
      item.classList.add("active");
      found = true;

      if (val !== "") {
        const regex = new RegExp(val, "gi");

        // SAFE highlight (doesn't break words)
        q.innerHTML = q.innerHTML.replace(regex, (m) => `<mark>${m}</mark>`);
        a.innerHTML = a.innerHTML.replace(regex, (m) => `<mark>${m}</mark>`);
      }
    } else {
      item.style.display = "none";
    }
  });

  noResult.style.display = found ? "none" : "block";
});

// ================= SCROLL ANIMATION (REPEAT) =================
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");
      } else {
        entry.target.classList.remove("show"); // repeat animation
      }
    });
  },
  { threshold: 0.2 },
);

items.forEach((item) => {
  item.classList.add("hidden");
  observer.observe(item);
});
