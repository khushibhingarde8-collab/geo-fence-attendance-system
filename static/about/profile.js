(function () {
  const slidesContainer = document.querySelector(".slides");
  const slides = document.querySelectorAll(".slide");
  const dotsContainer = document.querySelector(".slider-dots");

  if (!slidesContainer || slides.length === 0 || !dotsContainer) {
    console.log("Slider elements not found");
    return;
  }

  let currentIndex = 0;
  const totalSlides = slides.length;

  // Create dots
  slides.forEach((_, index) => {
    const dot = document.createElement("span");

    if (index === 0) dot.classList.add("active");

    dot.addEventListener("click", function () {
      currentIndex = index;
      updateSlider();
    });

    dotsContainer.appendChild(dot);
  });

  const dots = dotsContainer.querySelectorAll("span");

  function updateSlider() {
    slidesContainer.style.transform =
      "translateX(-" + currentIndex * 100 + "%)";

    dots.forEach((d) => d.classList.remove("active"));
    dots[currentIndex].classList.add("active");
  }

  // Auto slide
  setInterval(function () {
    currentIndex++;
    if (currentIndex >= totalSlides) currentIndex = 0;
    updateSlider();
  }, 4000);
})();