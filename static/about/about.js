// const observer = new IntersectionObserver(
//   (entries) => {
//     entries.forEach((entry) => {
//       if (entry.isIntersecting) {
//         entry.target.classList.add("show");
//       } else {
//         entry.target.classList.remove("show"); // repeat animation
//       }
//     });
//   },
//   {
//     threshold: 0.2,
//   },
// );

// document.querySelectorAll(".animate").forEach((el, index) => {
//   el.style.transitionDelay = `${index * 0.1}s`; // stagger
//   observer.observe(el);
// });

// const menuToggle = document.getElementById("menu-toggle");
// const navLinks = document.getElementById("nav-links");
// const closeMenu = document.getElementById("close-menu");

// menuToggle.onclick = () => {
//   navLinks.classList.add("active");
// };

// closeMenu.onclick = () => {
//   navLinks.classList.remove("active");
// };

// /* ABOUT DROPDOWN */

// const aboutToggle = document.querySelector(".mobile-dropdown-toggle");
// const aboutDropdown = document.querySelector(".about-dropdown");

// aboutToggle.onclick = () => {
//   aboutDropdown.classList.toggle("show");
// };

// /* ACCOUNT */

// const accountToggle = document.querySelectorAll(".mobile-dropdown-toggle")[1];
// const accountDropdown = document.querySelector(".dropdown");

// accountToggle.onclick = () => {
//   if (window.innerWidth <= 768) {
//     accountDropdown.classList.toggle("show");
//   }
// };

// document.querySelectorAll(".team-card").forEach((card) => {
//   card.addEventListener("mouseenter", () => {
//     card.classList.add("active");
//   });

//   card.addEventListener("mouseleave", () => {
//     card.classList.remove("active");
//   });
// });

/* ============================
   SCROLL ANIMATION
============================ */

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");
      } else {
        entry.target.classList.remove("show");
      }
    });
  },
  {
    threshold: 0.2,
  },
);

document.querySelectorAll(".animate").forEach((el, index) => {
  el.style.transitionDelay = `${index * 0.1}s`;

  observer.observe(el);
});

/* ============================
   MOBILE MENU
============================ */

const menuToggle = document.getElementById("menu-toggle");
const navLinks = document.getElementById("nav-links");
const closeMenu = document.getElementById("close-menu");

if (menuToggle && navLinks && closeMenu) {
  menuToggle.onclick = () => {
    navLinks.classList.add("active");
  };

  closeMenu.onclick = () => {
    navLinks.classList.remove("active");
  };
}

/* ============================
   ABOUT DROPDOWN
============================ */

const aboutToggle = document.querySelector(".mobile-dropdown-toggle");
const aboutDropdown = document.querySelector(".about-dropdown");

if (aboutToggle && aboutDropdown) {
  aboutToggle.onclick = () => {
    aboutDropdown.classList.toggle("show");
  };
}

/* ============================
   ACCOUNT DROPDOWN
============================ */

const dropdownToggles = document.querySelectorAll(".mobile-dropdown-toggle");
const accountDropdown = document.querySelector(".dropdown");

if (dropdownToggles.length > 1 && accountDropdown) {
  dropdownToggles[1].onclick = () => {
    if (window.innerWidth <= 768) {
      accountDropdown.classList.toggle("show");
    }
  };
}

/* ============================
   TEAM CARD HOVER
============================ */

document.querySelectorAll(".team-card").forEach((card) => {
  card.addEventListener("mouseenter", () => {
    card.classList.add("active");
  });

  card.addEventListener("mouseleave", () => {
    card.classList.remove("active");
  });
});

/* ============================
   IMAGE LAZY LOADING
============================ */

document.querySelectorAll("img").forEach((img) => {
  img.loading = "lazy";
});

/* ============================
   SMOOTH SCROLL
============================ */

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();

    const target = document.querySelector(this.getAttribute("href"));

    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
      });
    }
  });
});

/* ============================
   ACTIVE NAV LINK
============================ */

const currentPage = window.location.pathname;

document.querySelectorAll(".nav-links a").forEach((link) => {
  if (link.getAttribute("href") === currentPage) {
    link.classList.add("active");
  }
});

// =========================
// TEAM MODAL
// =========================

const modal = document.getElementById("teamModal");
const modalContent = document.getElementById("modalContent");

if (modal && modalContent) {
  window.openMember = function (card) {
    const image = card.querySelector("img").src;
    const name = card.querySelector(".member-name").innerText;
    const designation = card.querySelector(".member-designation").innerText;

    const popup = card.querySelector(".member-popup");

    const description = popup.querySelector("p").innerHTML;
    const details = popup.querySelector("ul").outerHTML;

    modalContent.innerHTML = `
      <img src="${image}" alt="${name}">
      <div class="member-details">
        <h3>${name}</h3>
        <h5>${designation}</h5>
        <p>${description}</p>
        ${details}
      </div>
    `;

    modal.classList.add("show");
    document.body.style.overflow = "hidden";
  };

  window.closeMember = function () {
    modal.classList.remove("show");
    document.body.style.overflow = "auto";
  };

  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      closeMember();
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeMember();
    }
  });
}
