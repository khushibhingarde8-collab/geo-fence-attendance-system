document.addEventListener("DOMContentLoaded", () => {
  const track = document.querySelector(".news-track");
  const items = document.querySelectorAll(".news-item");

  const box = document.getElementById("newsDetail");
  const titleEl = document.getElementById("detailTitle");
  const descEl = document.getElementById("detailDesc");
  const imgEl = document.getElementById("detailImg");
  const closeBtn = document.querySelector(".close-btn");

  let isBoxOpen = false;

  /* =========================
     PAUSE ONLY ON ITEM HOVER
  ========================= */
  items.forEach((item) => {
    item.addEventListener("mouseenter", () => {
      if (!isBoxOpen) {
        track.style.animationPlayState = "paused";
      }
    });

    item.addEventListener("mouseleave", () => {
      if (!isBoxOpen) {
        track.style.animationPlayState = "running";
      }
    });
  });

  /* =========================
     OPEN NEWS
  ========================= */
  function openNews(item) {
    isBoxOpen = true;

    track.style.animationPlayState = "paused";

    titleEl.innerText = item.dataset.title || "";
    descEl.innerText = item.dataset.desc || "";

    if (item.dataset.img) {
      imgEl.src = item.dataset.img;
      imgEl.style.display = "block";
    } else {
      imgEl.style.display = "none";
    }

    box.style.display = "block";
  }

  /* =========================
     CLOSE NEWS
  ========================= */
  function closeNews() {
    isBoxOpen = false;

    box.style.display = "none";

    track.style.animationPlayState = "running";
  }

  /* =========================
     EVENTS
  ========================= */
  items.forEach((item) => {
    item.addEventListener("click", () => openNews(item));
  });

  closeBtn.addEventListener("click", closeNews);
});
const counters = document.querySelectorAll(".counter");

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;

      const counter = entry.target;
      const target = +counter.dataset.target;

      let count = 0;
      const increment = Math.ceil(target / 50);

      function updateCount() {
        if (count < target) {
          count += increment;

          if (count > target) {
            count = target;
          }

          counter.innerHTML = count + "<span class='suffix'>+</span>";

          requestAnimationFrame(updateCount);
        } else {
          counter.innerHTML = target + "<span class='suffix'>+</span>";
        }
      }

      updateCount();

      observer.unobserve(counter);
    });
  },
  {
    threshold: 0.5,
  },
);

counters.forEach((counter) => observer.observe(counter));

const timelineItems = document.querySelectorAll(".timeline-item");
const timeline = document.querySelector(".timeline");

function showTimelineItems() {
  const triggerBottom = window.innerHeight * 0.85;

  timelineItems.forEach((item) => {
    const itemTop = item.getBoundingClientRect().top;

    if (itemTop < triggerBottom) {
      item.classList.add("show");
      timeline.classList.add("animate-line");
    }
  });
}

window.addEventListener("scroll", showTimelineItems);

showTimelineItems();

const certRows = document.querySelectorAll(".cert-row");

function showCerts() {
  const triggerBottom = window.innerHeight * 0.85;

  certRows.forEach((row) => {
    const rowTop = row.getBoundingClientRect().top;

    if (rowTop < triggerBottom) {
      row.classList.add("show");
    }
  });
}

window.addEventListener("scroll", showCerts);

showCerts();

function openModal(src) {
  const modal = document.getElementById("certModal");
  const img = document.getElementById("modalImg");

  img.onload = function () {
    modal.scrollTop = 0;
  };

  img.src = src;
  modal.style.display = "block";
}

function closeModal() {
  document.getElementById("certModal").style.display = "none";
}

const cards = document.querySelectorAll(".gallery-card");

function showGallery() {
  const trigger = window.innerHeight * 0.85;

  cards.forEach((card) => {
    const top = card.getBoundingClientRect().top;

    if (top < trigger) {
      card.classList.add("show");
    }
  });
}

window.addEventListener("scroll", showGallery);
showGallery();

function openGallery() {
  document.getElementById("galleryModal").style.display = "block";
}

function closeGallery() {
  document.getElementById("galleryModal").style.display = "none";
}

const counters1 = document.querySelectorAll(".counter");

counters1.forEach((counter) => {
  const updateCount = () => {
    const target = +counter.getAttribute("data-target");
    const count = +counter.innerText;

    const speed = 50;

    const increment = target / speed;

    if (count < target) {
      counter.innerText = Math.ceil(count + increment);
      setTimeout(updateCount, 40);
    } else {
      counter.innerText = target + "+";
    }
  };

  updateCount();
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

const ticker = document.querySelector(".news-scroll");

const newsItems = document.querySelectorAll(".news-item");

newsItems.forEach((item) => {
  item.addEventListener("mouseenter", () => {
    ticker.classList.add("pause");
  });

  item.addEventListener("mouseleave", () => {
    ticker.classList.remove("pause");
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const track = document.querySelector(".news-track");
  const items = document.querySelectorAll(".news-item");

  const box = document.getElementById("newsDetail");
  const titleEl = document.getElementById("detailTitle");
  const descEl = document.getElementById("detailDesc");
  const imgEl = document.getElementById("detailImg");
  const closeBtn = document.querySelector(".close-btn");

  let isOpen = false;

  function openNews(item) {
    isOpen = true;

    track.classList.add("pause");

    titleEl.innerText = item.dataset.title;
    descEl.innerText = item.dataset.desc;

    const img = item.dataset.img;

    if (img && img.trim() !== "") {
      imgEl.src = img;
      imgEl.style.display = "block";
    } else {
      imgEl.style.display = "none";
    }

    box.style.display = "block";
  }

  function closeNews() {
    isOpen = false;

    box.style.display = "none";
    track.classList.remove("pause");
  }

  items.forEach((item) => {
    item.addEventListener("mouseenter", () => {
      if (!isOpen) track.classList.add("pause");
    });

    item.addEventListener("mouseleave", () => {
      if (!isOpen) track.classList.remove("pause");
    });

    item.addEventListener("click", () => openNews(item));
  });

  closeBtn.addEventListener("click", closeNews);
});
function fillNews(title, desc, img) {
  const fakeItem = {
    dataset: {
      title: title,
      desc: desc,
      img: img,
    },
  };

  openNews(fakeItem);
}

function fillCertificate(id, title, description) {
  document.getElementById("certificate_id").value = id;
  document.getElementById("certificate_title").value = title;
  document.getElementById("certificate_description").value = description;
}

function clearCertificateForm() {
  document.getElementById("certificate_id").value = "";
  document.getElementById("certificate_title").value = "";
  document.getElementById("certificate_description").value = "";

  document.querySelector('input[name="image"]').value = "";
  document.querySelector('input[name="pdf"]').value = "";
}

const filterButtons = document.querySelectorAll(".filter-btn");
const galleryItems = document.querySelectorAll(".gallery-item");

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    filterButtons.forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");

    const filter = button.dataset.filter;

    galleryItems.forEach((item) => {
      if (filter === "all" || item.dataset.category === filter) {
        item.style.display = "block";
      } else {
        item.style.display = "none";
      }
    });
  });
});