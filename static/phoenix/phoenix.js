document.addEventListener("DOMContentLoaded", () => {
  // ================================
  // HERO
  // ================================
  const hero = document.querySelector(".phoenix-hero");

  if (hero) {
    const heroObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            hero.classList.add("show");
          } else {
            hero.classList.remove("show");
          }
        });
      },
      { threshold: 0.2 },
    );

    heroObserver.observe(hero);
  }

  // ================================
  // PRODUCT SECTION
  // ================================
  const productSection = document.querySelector(".phoenix-container");
  const productCards = document.querySelectorAll(".phoenix-card");

  if (productSection) {
    const productObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            productSection.classList.add("show");

            productCards.forEach((card, index) => {
              setTimeout(() => {
                card.classList.add("show");
              }, index * 150);
            });
          }
        });
      },
      { threshold: 0.2 },
    );

    productObserver.observe(productSection);
  }

  // ================================
  // WHY SECTION
  // ================================
  const whySection = document.querySelector(".why-section");
  const whyBoxes = document.querySelectorAll(".why-box");

  if (whySection) {
    const whyObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            whySection.classList.add("show");

            whyBoxes.forEach((box, index) => {
              setTimeout(() => {
                box.classList.add("show");
              }, index * 150);
            });
          } else {
            whySection.classList.remove("show");

            whyBoxes.forEach((box) => {
              box.classList.remove("show");
            });
          }
        });
      },
      { threshold: 0.2 },
    );

    whyObserver.observe(whySection);
  }
});

// ================================
// CATALOG FIXED ANIMATION
// ================================
const catalogPage = document.querySelector(".catalog-page");
const pdfLeft = document.querySelector(".pdf-left");
const pdfRight = document.querySelector(".pdf-right");

if (catalogPage) {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          catalogPage.classList.add("show");

          // 🔥 trigger separately
          setTimeout(() => {
            pdfLeft.classList.add("show");
          }, 200);

          setTimeout(() => {
            pdfRight.classList.add("show");
          }, 400);
        } else {
          catalogPage.classList.remove("show");

          pdfLeft.classList.remove("show");
          pdfRight.classList.remove("show");
        }
      });
    },
    { threshold: 0.3 },
  ); // 👈 slightly higher

  observer.observe(catalogPage);
}
// ================================
// Expand Card on Click (Optional)
// ================================
function goToProduct(category) {
  window.location.href = "/product-detail?product=" + category;
}

// ================================
// CERTIFICATE SECTION ANIMATION
// ================================
const certSection = document.querySelector(".certificate-section");
const certCards = document.querySelectorAll(".certificate-card");

if (certSection) {
  const certObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          certSection.classList.add("show");

          certCards.forEach((card, index) => {
            setTimeout(() => {
              card.classList.add("show");
            }, index * 150);
          });
        } else {
          // 🔁 repeat animation every scroll
          certSection.classList.remove("show");

          certCards.forEach((card) => {
            card.classList.remove("show");
          });
        }
      });
    },
    { threshold: 0.2 },
  );

  certObserver.observe(certSection);
}

// ================================
// CERTIFICATE POPUP
// ================================
const popup = document.getElementById("certPopup");
const popupImg = document.getElementById("popupImg");
const closeBtn = document.querySelector(".close-btn");

certCards.forEach((card) => {
  card.addEventListener("click", () => {
    const imgSrc = card.querySelector("img").src;
    popupImg.src = imgSrc;
    popup.classList.add("active");
  });
});

closeBtn.addEventListener("click", () => {
  popup.classList.remove("active");
});

// close on outside click
popup.addEventListener("click", (e) => {
  if (e.target === popup) {
    popup.classList.remove("active");
  }
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
