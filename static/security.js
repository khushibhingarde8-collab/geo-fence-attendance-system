/* ===================================================
   🔒 WEBSITE SECURITY & CONTENT PROTECTION
=================================================== */

/* ==============================
   DISABLE RIGHT CLICK
============================== */
document.addEventListener("contextmenu", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE TEXT SELECTION
============================== */
document.addEventListener("selectstart", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE DRAGGING (IMAGES/TEXT)
============================== */
document.addEventListener("dragstart", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE COPY
============================== */
document.addEventListener("copy", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE CUT
============================== */
document.addEventListener("cut", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE PASTE
============================== */
document.addEventListener("paste", (e) => {
  e.preventDefault();
});

/* ==============================
   BLOCK KEYBOARD SHORTCUTS
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

  // CTRL + SHIFT + C
  if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "c") {
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

  // CTRL + S
  if (e.ctrlKey && e.key.toLowerCase() === "s") {
    e.preventDefault();
  }

  // CTRL + C
  if (e.ctrlKey && e.key.toLowerCase() === "c") {
    e.preventDefault();
  }

  // CTRL + X
  if (e.ctrlKey && e.key.toLowerCase() === "x") {
    e.preventDefault();
  }
});

/* ==============================
   DISABLE IMAGE DRAG
============================== */
document.querySelectorAll("img").forEach((img) => {
  img.setAttribute("draggable", "false");
});

/* ==============================
   DEVTOOLS DETECTION
============================== */
(function () {
  function detectDevTools() {
    const widthThreshold = window.outerWidth - window.innerWidth > 160;
    const heightThreshold = window.outerHeight - window.innerHeight > 160;

    if (widthThreshold || heightThreshold) {
      document.body.innerHTML = `
                <div style="
                    height:100vh;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    flex-direction:column;
                    font-family:Arial;
                    background:#0b0a24;
                    color:white;
                    text-align:center;
                    padding:20px;
                ">
                    <h1>Access Restricted</h1>
                    <p>Developer tools are disabled on this website.</p>
                </div>
            `;
    }
  }

  setInterval(detectDevTools, 1000);
})();

/* ==============================
   DISABLE CONSOLE LOG ACCESS
============================== */
console.log = function () {};
console.warn = function () {};
console.error = function () {};
console.info =
  function () {}; /* ===================================================
   🔒 WEBSITE SECURITY & CONTENT PROTECTION
=================================================== */

/* ==============================
   DISABLE RIGHT CLICK
============================== */
document.addEventListener("contextmenu", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE TEXT SELECTION
============================== */
document.addEventListener("selectstart", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE DRAGGING (IMAGES/TEXT)
============================== */
document.addEventListener("dragstart", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE COPY
============================== */
document.addEventListener("copy", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE CUT
============================== */
document.addEventListener("cut", (e) => {
  e.preventDefault();
});

/* ==============================
   DISABLE PASTE
============================== */
document.addEventListener("paste", (e) => {
  e.preventDefault();
});

/* ==============================
   BLOCK KEYBOARD SHORTCUTS
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

  // CTRL + SHIFT + C
  if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "c") {
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

  // CTRL + S
  if (e.ctrlKey && e.key.toLowerCase() === "s") {
    e.preventDefault();
  }

  // CTRL + C
  if (e.ctrlKey && e.key.toLowerCase() === "c") {
    e.preventDefault();
  }

  // CTRL + X
  if (e.ctrlKey && e.key.toLowerCase() === "x") {
    e.preventDefault();
  }
});

/* ==============================
   DISABLE IMAGE DRAG
============================== */
document.querySelectorAll("img").forEach((img) => {
  img.setAttribute("draggable", "false");
});

/* ==============================
   DEVTOOLS DETECTION
============================== */
(function () {
  function detectDevTools() {
    const widthThreshold = window.outerWidth - window.innerWidth > 160;
    const heightThreshold = window.outerHeight - window.innerHeight > 160;

    if (widthThreshold || heightThreshold) {
      document.body.innerHTML = `
                <div style="
                    height:100vh;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    flex-direction:column;
                    font-family:Arial;
                    background:#0b0a24;
                    color:white;
                    text-align:center;
                    padding:20px;
                ">
                    <h1>Access Restricted</h1>
                    <p>Developer tools are disabled on this website.</p>
                </div>
            `;
    }
  }

  setInterval(detectDevTools, 1000);
})();

/* ==============================
   DISABLE CONSOLE LOG ACCESS
============================== */
console.log = function () {};
console.warn = function () {};
console.error = function () {};
console.info = function () {};
