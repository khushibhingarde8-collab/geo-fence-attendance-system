/* ================= SCROLL ANIMATION SYSTEM ================= */

function handleScrollAnimation(selector) {
  const elements = document.querySelectorAll(selector);

  window.addEventListener("scroll", () => {
    const triggerTop = window.innerHeight * 0.85;
    const triggerBottom = window.innerHeight * 0.2;

    elements.forEach((el) => {
      const rect = el.getBoundingClientRect();

      if (rect.top < triggerTop && rect.bottom > triggerBottom) {
        el.classList.add("show");
      } else {
        el.classList.remove("show");
      }
    });
  });
}

/* APPLY ANIMATIONS */

handleScrollAnimation(".services-container");
handleScrollAnimation(".service-header");
handleScrollAnimation(".service-left");
handleScrollAnimation(".service-right");
handleScrollAnimation(".service-card");
handleScrollAnimation(".testimonial-section");
handleScrollAnimation(".testimonial-left");
handleScrollAnimation(".testimonial-right");

/* ================= SERVICE CARD CLICK ================= */

const serviceCards = document.querySelectorAll(".service-card");

serviceCards.forEach((card) => {
  card.addEventListener("click", () => {
    serviceCards.forEach((c) => c.classList.remove("active"));
    card.classList.toggle("active");
  });
});

/* ================= TESTIMONIAL SLIDER ================= */

const slides = document.querySelectorAll(".slides");
let index = 0;

function showSlide(i) {
  slides.forEach((slide) => slide.classList.remove("active"));
  slides[i].classList.add("active");
}

setInterval(() => {
  index++;
  if (index >= slides.length) {
    index = 0;
  }

  showSlide(index);
}, 3000);

const menuToggle = document.getElementById("menu-toggle");
const navLinks = document.getElementById("nav-links");
const closeMenu = document.getElementById("close-menu");

menuToggle.onclick = () => {
  navLinks.classList.add("active");
};

closeMenu.onclick = () => {
  navLinks.classList.remove("active");
};

/* ABOUT DROPDOWN */

const aboutToggle = document.querySelector(".mobile-dropdown-toggle");
const aboutDropdown = document.querySelector(".about-dropdown");

aboutToggle.onclick = () => {
  aboutDropdown.classList.toggle("show");
};

/* ACCOUNT */

const accountToggle = document.querySelectorAll(".mobile-dropdown-toggle")[1];
const accountDropdown = document.querySelector(".dropdown");

accountToggle.onclick = () => {
  if (window.innerWidth <= 768) {
    accountDropdown.classList.toggle("show");
  }
};
