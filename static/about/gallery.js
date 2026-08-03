const allImages = document.querySelectorAll(".gallery-item img");
const lightbox = document.getElementById("lightbox");
const lightboxImg = document.getElementById("lightbox-img");

const closeBtn = document.querySelector(".close");
const prevBtn = document.querySelector(".prev");
const nextBtn = document.querySelector(".next");

let currentIndex = 0;
let visibleImages = [];

// Open Lightbox
allImages.forEach((img) => {
  img.addEventListener("click", () => {
    visibleImages = Array.from(
      document.querySelectorAll(".gallery-item:not(.hide) img"),
    );

    currentIndex = visibleImages.indexOf(img);

    lightbox.style.display = "flex";
    lightboxImg.src = visibleImages[currentIndex].src;
  });
});

// Close
closeBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  lightbox.style.display = "none";
});

// Close on background click
lightbox.addEventListener("click", (e) => {
  if (e.target === lightbox) {
    lightbox.style.display = "none";
  }
});

// Previous
prevBtn.addEventListener("click", (e) => {
  e.stopPropagation();

  currentIndex =
    (currentIndex - 1 + visibleImages.length) % visibleImages.length;

  lightboxImg.src = visibleImages[currentIndex].src;
});

// Next
nextBtn.addEventListener("click", (e) => {
  e.stopPropagation();

  currentIndex = (currentIndex + 1) % visibleImages.length;

  lightboxImg.src = visibleImages[currentIndex].src;
});

// Filters
const filterButtons = document.querySelectorAll(".filter-btn");
const galleryItems = document.querySelectorAll(".gallery-item");

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    filterButtons.forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");

    const filter = button.dataset.filter;

    galleryItems.forEach((item) => {
      if (filter === "all" || item.dataset.category === filter) {
        item.classList.remove("hide");
      } else {
        item.classList.add("hide");
      }
    });
  });
});