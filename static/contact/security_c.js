/* ===================================================
   LIGHT SECURITY FOR CONTACT PAGE
=================================================== */

/* ==============================
   DISABLE RIGHT CLICK
============================== */
document.addEventListener("contextmenu", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE IMAGE DRAGGING
============================== */
document.querySelectorAll("img").forEach((img) => {
  img.setAttribute("draggable", "false");
});

/* ==============================
   BLOCK FEW SHORTCUTS
============================== */
document.addEventListener("keydown", (e) => {
  // F12
  if (e.key === "F12") {
    e.preventDefault();
  }

  // CTRL + SHIFT + I
  if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "i") {
    e.preventDefault();
  }

  // CTRL + SHIFT + J
  if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "j") {
    e.preventDefault();
  }

  // CTRL + U
  if (e.ctrlKey && e.key.toLowerCase() === "u") {
    e.preventDefault();
  }
});
