/* ================= PROJECT CARD ANIMATION ================= */

const cards = document.querySelectorAll(".project-card");

function animateCards() {

    const trigger = window.innerHeight * 0.85;

    cards.forEach((card, index) => {

        const rect = card.getBoundingClientRect();

        if (rect.top < trigger) {

            setTimeout(() => {
                card.classList.add("show");
            }, index * 150);

        }

    });

}

window.addEventListener("scroll", animateCards);
window.addEventListener("load", animateCards);

/* ================= MOBILE MENU ================= */

const menuToggle = document.getElementById("menu-toggle");
const navLinks = document.getElementById("nav-links");
const closeMenu = document.getElementById("close-menu");

if (menuToggle && navLinks) {

    menuToggle.onclick = () => {
        navLinks.classList.add("active");
    };

}

if (closeMenu && navLinks) {

    closeMenu.onclick = () => {
        navLinks.classList.remove("active");
    };

}

/* ================= ABOUT DROPDOWN ================= */

const aboutToggle = document.querySelector(".mobile-dropdown-toggle");
const aboutDropdown = document.querySelector(".about-dropdown");

if (aboutToggle && aboutDropdown) {

    aboutToggle.onclick = () => {
        aboutDropdown.classList.toggle("show");
    };

}

/* ================= ACCOUNT DROPDOWN ================= */

const accountToggle = document.querySelectorAll(".mobile-dropdown-toggle")[1];
const accountDropdown = document.querySelector(".dropdown");

if (accountToggle && accountDropdown) {

    accountToggle.onclick = () => {

        if (window.innerWidth <= 768) {
            accountDropdown.classList.toggle("show");
        }

    };

}