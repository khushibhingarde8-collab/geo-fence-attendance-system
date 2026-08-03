
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
