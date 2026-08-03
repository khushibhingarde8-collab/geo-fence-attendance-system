let slides = document.querySelectorAll(".slide");
let index = 0;

setInterval(() => {
  slides[index].classList.remove("active");
  index = (index + 1) % slides.length;
  slides[index].classList.add("active");
}, 3000);

window.addEventListener("load", function () {
  const loader = document.getElementById("preloader");
  loader.style.opacity = "0";
  loader.style.transition = "opacity 10s ease";

  setTimeout(() => {
    loader.style.display = "none";
  }, 600);
});
