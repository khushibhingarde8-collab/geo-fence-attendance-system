// ===== TEAM DATA (ADMIN READY STRUCTURE) =====
const teamMembers = [
  {
    name: "Owner",
    role: "Owner",
    image: "images_team/ceo.jpg",
  },
  {
    name: "Rizwan Rayeen",
    role: "Engineer",
    image: "images_team/manager.jpg",
  },
  {
    name: "Samrat Sau",
    role: "Head Project",
    image: "images_team/guide.jpg",
  },
  {
    name: "Md.Asif Eqbal",
    role: "Instrummentation Design Engineer",
    image: "images_team/guide.jpg",
  },
  {
    name: "Shadab",
    role: "Instrummentation Design Engineer",
    image: "images_team/guide.jpg",
  },
  {
    name: "Sindhu Devraj",
    role: "Sr.Instrumentation Engineer",
    image: "images_team/guide.jpg",
  },
  {
    name: "Vinoth Bhaskaran",
    role: "Associate Engineer",
    image: "images_team/guide.jpg",
  },
];

// ===== RENDER TEAM =====
const teamContainer = document.getElementById("team-container");

if (teamContainer) {
  teamContainer.innerHTML = "";

  teamMembers.forEach((member) => {
    const card = document.createElement("div");
    card.className = "team-card";

    card.innerHTML = `
      <img src="${member.image}">
      <h4>${member.name}</h4>
      <p>${member.role}</p>
    `;

    teamContainer.appendChild(card);
  });

  // 🔥 ADD THIS LINE
  teamContainer.innerHTML += teamContainer.innerHTML;
}

// ================= SCROLL ANIMATION (FOR ALL SECTIONS, REPEATABLE) =================

function scrollAnimation() {
  const elements = document.querySelectorAll(
    ".detail-left, .detail-right, .animate-left, .animate-right, .animate-up, .animate-blur, section-animate",
  );

  window.addEventListener("scroll", () => {
    const trigger = window.innerHeight * 0.85;

    elements.forEach((el) => {
      const rect = el.getBoundingClientRect();

      if (rect.top < trigger && rect.bottom > 0) {
        el.classList.add("show"); // show when visible
      } else {
        el.classList.remove("show"); // reset when out
      }
    });
  });
}

scrollAnimation();

// ===== SECTION ANIMATION (REPEATABLE) =====

function sectionAnimation() {
  const sections = document.querySelectorAll(".section-animate");

  window.addEventListener("scroll", () => {
    const trigger = window.innerHeight * 0.85;

    sections.forEach((sec) => {
      const rect = sec.getBoundingClientRect();

      if (rect.top < trigger && rect.bottom > 0) {
        sec.classList.add("show");
      } else {
        sec.classList.remove("show");
      }
    });
  });
}

sectionAnimation();

document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menu-toggle");
  const navLinks = document.getElementById("nav-links");
  const closeMenu = document.getElementById("close-menu");

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      navLinks.classList.add("active");
    });
  }

  if (closeMenu && navLinks) {
    closeMenu.addEventListener("click", () => {
      navLinks.classList.remove("active");
    });
  }

  const aboutToggle = document.querySelector(".mobile-dropdown-toggle");
  const aboutDropdown = document.querySelector(".about-dropdown");

  if (aboutToggle && aboutDropdown) {
    aboutToggle.addEventListener("click", () => {
      aboutDropdown.classList.toggle("show");
    });
  }
});
