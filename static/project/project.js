const section = document.querySelector(".services-container");

if (section) {
  window.addEventListener("scroll", () => {
    const triggerTop = window.innerHeight * 0.85;
    const triggerBottom = window.innerHeight * 0.2;

    const rect = section.getBoundingClientRect();

    if (rect.top < triggerTop && rect.bottom > triggerBottom) {
      section.classList.add("show");
    } else {
      section.classList.remove("show");
    }
  });
}

/* for the cards */
const cards = document.querySelectorAll(".card");

window.addEventListener("scroll", () => {
  cards.forEach((card) => {
    const triggerTop = window.innerHeight * 0.85;
    const triggerBottom = window.innerHeight * 0.2;

    const rect = card.getBoundingClientRect();

    if (rect.top < triggerTop && rect.bottom > triggerBottom) {
      card.classList.add("show");
    } else {
      card.classList.remove("show"); // 🔥 reset
    }
  });
});

/* for the section animation */
const header = document.querySelector(".project-header");
const left = document.querySelector(".project-left");
const right = document.querySelector(".project-right");

if (header && left && right) {
  window.addEventListener("scroll", () => {
    const trigger = window.innerHeight * 0.8;
    const rect = header.getBoundingClientRect();

    if (rect.top < trigger && rect.bottom > 100) {
      header.classList.add("show");
      left.classList.add("show");
      right.classList.add("show");
    } else {
      header.classList.remove("show");
      left.classList.remove("show");
      right.classList.remove("show");
    }
  });
}
/* the circle */

const container = document.getElementById("logoTrack");

const visibleCount = 10;
const radius = 200;
const speed = 0.002;

let offset = 0;
let globalIndex = visibleCount;

const items = [];

/* INIT */
function init() {
  for (let i = 0; i < visibleCount; i++) {
    const img = document.createElement("img");
    img.src = logos[i];
    img._changed = false;
    container.appendChild(img);
    items.push(img);
  }
}

/* ANIMATION */
function animate() {
  const arcStart = 0;
  const arcEnd = Math.PI * 2;
  const arcLength = arcEnd - arcStart;

  for (let i = 0; i < items.length; i++) {
    let progress = i / items.length + offset;

    if (progress >= 1) {
      progress -= 1;

      if (!items[i]._changed) {
        items[i].src = logos[globalIndex % logos.length];
        globalIndex++;
        items[i]._changed = true;
      }
    } else {
      items[i]._changed = false;
    }

    const angle = arcStart + progress * arcLength;

    const x = radius * Math.cos(angle);
    const y = radius * Math.sin(angle);

    // 🔥 3D DEPTH EFFECT
    const depth = (Math.sin(angle) + 1) / 2; // 0 → back, 1 → front

    const scale = 1 + depth * 0.3; // front bigger
    const opacity = 0.5 + depth * 0.5; // front brighter
    const zIndex = Math.floor(depth * 100);

    items[i].style.left = `calc(50% + ${x}px - 35px)`;
    items[i].style.top = `calc(50% + ${y}px - 35px)`;

    items[i].style.transform = `scale(${scale})`;
    items[i].style.opacity = opacity;
    items[i].style.zIndex = zIndex;
  }

  offset += speed;
  if (offset >= 1) offset = 0;

  requestAnimationFrame(animate);
}

/* RUN */
init();
animate();

/* ================= RENDER ================= */

/* ================= POPUP UPDATE ================= */

function openPopup(
    id,
    title,
    company,
    category,
    duration,
    shortDesc
){

    document.getElementById("popupTitle").innerText = title;

    document.getElementById("popupDesc").innerHTML = `
        <b>Company:</b> ${company}<br><br>

        <b>Category:</b> ${category}<br><br>

        <b>Duration:</b> ${duration}<br><br>

        <b>About:</b><br>

        ${shortDesc}

        <br><br>

        <button
            class="popup-btn"
            onclick="goDetail(${id})">

            View Full Details →

        </button>
    `;

    document.getElementById("popup").classList.add("show");

}

function goDetail(id) {
  window.location.href = "/project-detail?id=" + id;
}

function closePopup() {
  const popup = document.getElementById("popup");
  if (popup) popup.classList.remove("show");
}

const sliderSection = document.querySelector(".project-slider-section");

if (sliderSection) {
  window.addEventListener("scroll", () => {
    const triggerTop = window.innerHeight * 0.85;
    const triggerBottom = window.innerHeight * 0.2;

    const rect = sliderSection.getBoundingClientRect();

    if (rect.top < triggerTop && rect.bottom > triggerBottom) {
      sliderSection.classList.add("show");
    } else {
      sliderSection.classList.remove("show");
    }
  });
}

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
