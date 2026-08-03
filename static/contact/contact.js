const faqItems = document.querySelectorAll(".faq-item");

faqItems.forEach((item) => {
  const question = item.querySelector(".faq-question");
  const answer = item.querySelector(".faq-answer");
  question.addEventListener("click", () => {
    // close all
    faqItems.forEach((faq) => {
      if (faq !== item) {
        faq.classList.remove("active");
      }
    });

    // toggle current
    item.classList.toggle("active");
  });
});

const animatedElements = document.querySelectorAll(".animate");
document.addEventListener("DOMContentLoaded", function () {
  const animatedElements = document.querySelectorAll(".animate");
  function checkScroll() {
    const triggerBottom = window.innerHeight * 0.85;
    animatedElements.forEach((el) => {
      const elementTop = el.getBoundingClientRect().top;
      const elementBottom = el.getBoundingClientRect().bottom;
      if (elementTop < triggerBottom && elementBottom > 0) {
        el.classList.add("show"); // animate
      } else {
        el.classList.remove("show"); // reset animation
      }
    });
  }
  window.addEventListener("scroll", checkScroll);
  checkScroll(); // run once on load
});
const faqCards = document.querySelectorAll(".faq-item");

faqCards.forEach((card, index) => {
  card.style.transitionDelay = `${index * 0.15}s`;
});

const form = document.getElementById("contactForm");
const successMsg = document.querySelector(".success-msg");

form.addEventListener("submit", function () {
  setTimeout(() => {
    successMsg.style.display = "block";

    form.reset();

    setTimeout(() => {
      successMsg.style.display = "none";
    }, 4000);
  }, 1000);
});

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
