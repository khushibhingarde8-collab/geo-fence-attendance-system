/* title animation */
const textElements = document.querySelectorAll(".reveal-text");

function revealTextOnScroll() {
  const trigger = window.innerHeight * 0.85;

  textElements.forEach((el) => {
    const top = el.getBoundingClientRect().top;

    if (top < trigger) {
      el.classList.add("show");
    } else {
      el.classList.remove("show"); // re-animate
    }
  });
}

window.addEventListener("scroll", revealTextOnScroll);
window.addEventListener("load", revealTextOnScroll);

const section = document.querySelector(".clients-section");

function revealSection() {
  const trigger = window.innerHeight * 0.8;
  const top = section.getBoundingClientRect().top;

  if (top < trigger) {
    section.classList.add("show");
  } else {
    section.classList.remove("show");
  }
}

window.addEventListener("scroll", revealSection);

const cards = document.querySelectorAll(".client-card");
function revealWave() {
  const trigger = window.innerHeight * 0.85;
  cards.forEach((card) => {
    const rect = card.getBoundingClientRect();
    if (rect.top < trigger && rect.bottom > 0) {
      // diagonal delay
      const delay = (rect.left + rect.top) * 0.15;
      setTimeout(() => {
        card.classList.add("show");
      }, delay);
    } else {
      // 🔥 REMOVE CLASS WHEN OUT OF VIEW
      card.classList.remove("show");
    }
  });
}

window.addEventListener("scroll", revealWave);
window.addEventListener("load", revealWave);

/* box random direction */
const sections = document.querySelectorAll(".animate-section");

function revealSections() {
  const trigger = window.innerHeight * 0.8;

  sections.forEach((sec) => {
    const top = sec.getBoundingClientRect().top;

    if (top < trigger) {
      sec.classList.add("show");
    } else {
      sec.classList.remove("show");
    }
  });
}

window.addEventListener("scroll", revealSections);
const slideElements = document.querySelectorAll(".slide-left, .slide-right");

function revealSlide() {
  const trigger = window.innerHeight * 0.85;

  slideElements.forEach((el) => {
    const top = el.getBoundingClientRect().top;

    if (top < trigger) {
      el.classList.add("show");
    } else {
      el.classList.remove("show"); // re-trigger on scroll
    }
  });
}

window.addEventListener("scroll", revealSlide);
window.addEventListener("load", revealSlide);

// ================= what our client say animation =================
window.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("testimonialContainer");
  const cards = document.querySelectorAll(".testimonial-card");

  let isPaused = false;
  let isDragging = false;
  let startX, scrollLeft;

  /* AUTO SCROLL */
  function autoScroll() {
    if (!isPaused && !isDragging) {
      container.scrollLeft += 1.5;
    }

    if (container.scrollLeft >= container.scrollWidth / 2) {
      container.scrollLeft = 0;
    }

    highlightCenter();

    requestAnimationFrame(autoScroll);
  }

  /* CENTER DETECT */
  function highlightCenter() {
    const center = container.scrollLeft + container.offsetWidth / 2;

    cards.forEach((card) => {
      const cardCenter = card.offsetLeft + card.offsetWidth / 2;

      if (Math.abs(center - cardCenter) < card.offsetWidth / 2) {
        card.classList.add("active");
      } else {
        card.classList.remove("active");
      }
    });
  }

  /* HOVER PAUSE */
  container.addEventListener("mouseenter", () => (isPaused = true));
  container.addEventListener("mouseleave", () => (isPaused = false));

  /* DRAG SCROLL (INSANE UX) */
  let scrollTimeout;

  container.addEventListener("scroll", () => {
    clearTimeout(scrollTimeout);

    scrollTimeout = setTimeout(() => {
      const center = container.scrollLeft + container.offsetWidth / 2;

      let closestCard = null;
      let minDistance = Infinity;

      cards.forEach((card) => {
        const cardCenter = card.offsetLeft + card.offsetWidth / 2;
        const distance = Math.abs(center - cardCenter);

        if (distance < minDistance) {
          minDistance = distance;
          closestCard = card;
        }
      });

      if (closestCard) {
        container.scrollTo({
          left:
            closestCard.offsetLeft -
            container.offsetWidth / 2 +
            closestCard.offsetWidth / 2,
          behavior: "smooth",
        });
      }
    }, 100);
  });
  container.addEventListener("mousedown", (e) => {
    isDragging = true;
    startX = e.pageX - container.offsetLeft;
    scrollLeft = container.scrollLeft;
  });

  container.addEventListener("mouseleave", () => (isDragging = false));
  container.addEventListener("mouseup", () => (isDragging = false));

  container.addEventListener("mousemove", (e) => {
    if (!isDragging) return;

    e.preventDefault();
    const x = e.pageX - container.offsetLeft;
    const walk = (x - startX) * 2;

    container.scrollLeft = scrollLeft - walk;
  });

  autoScroll();
});

const allCards = document.querySelectorAll(".testimonial-card");

allCards.forEach((card) => {
  card.addEventListener("mousemove", (e) => {
    const rect = card.getBoundingClientRect();

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const rotateX = (y / rect.height - 0.5) * -15;
    const rotateY = (x / rect.width - 0.5) * 15;

    card.style.transform = `scale(1.1) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
  });

  card.addEventListener("mouseleave", () => {
    card.style.transform = "";
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const container = document.getElementById("testimonialContainer");

  if (!container) return;

  /* 🔥 AUTO CLONE CONTENT */
  container.innerHTML += container.innerHTML;

  let speed = 0.6;
  let isPaused = false;

  function scrollLoop() {
    if (!isPaused) {
      container.scrollLeft += speed;
    }

    /* 🔥 PERFECT LOOP */
    if (container.scrollLeft >= container.scrollWidth / 2) {
      container.scrollLeft -= container.scrollWidth / 2;
    }

    requestAnimationFrame(scrollLoop);
  }

  /* PAUSE ON HOVER */
  container.addEventListener("mouseenter", () => (isPaused = true));
  container.addEventListener("mouseleave", () => (isPaused = false));

  scrollLoop();
});
const testimonialSection = document.querySelector(".testimonial-section");
const testimonialCards = document.querySelectorAll(".testimonial-card");

function handleTestimonialAnimation() {
  const sectionTop = testimonialSection.getBoundingClientRect().top;
  const sectionBottom = testimonialSection.getBoundingClientRect().bottom;
  const windowHeight = window.innerHeight;

  if (sectionTop < windowHeight && sectionBottom > 0) {
    // Section is visible → add class
    testimonialSection.classList.add("show");

    testimonialCards.forEach((card, index) => {
      setTimeout(() => {
        card.classList.add("show");
      }, index * 200);
    });
  } else {
    // Section is out of view → remove class to re-trigger animation
    testimonialSection.classList.remove("show");
    testimonialCards.forEach((card) => card.classList.remove("show"));
  }
}

window.addEventListener("scroll", handleTestimonialAnimation);
window.addEventListener("load", handleTestimonialAnimation);

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
