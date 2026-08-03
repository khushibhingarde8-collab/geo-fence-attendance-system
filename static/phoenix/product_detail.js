// ================================
// WAIT FOR FULL LOAD (IMPORTANT)
// ================================
document.addEventListener("DOMContentLoaded", () => {
  // ================================
  // GET PRODUCT FROM URL
  // ================================
  const params = new URLSearchParams(window.location.search);
  const product = params.get("product");

  // ELEMENTS
  const title = document.getElementById("title");
  const desc = document.getElementById("desc");
  const img = document.getElementById("img");
  const featuresBox = document.getElementById("features");
  const advantagesBox = document.getElementById("advantages");
  const specsBox = document.getElementById("specs");

  // ================================
  // PRODUCT DATA
  // ================================
  const data = {
    spd: {
      title: "Surge Protection Devices",
      desc: "Phoenix Contact products are designed to deliver reliable and intelligent industrial automation solutions across a wide range of applications. These products ensure seamless power distribution, signal processing, and communication within complex systems. Built with advanced engineering standards, they provide consistent performance even in harsh industrial environments, making them ideal for manufacturing, energy, and infrastructure sectors. With a strong focus on innovation and safety, Phoenix Contact integrates modern technologies such as smart monitoring, surge protection, and high-speed networking into their devices.",
      img: "images/spd.jpg",
      features: [
        "Pluggable surge protection modules",
        "Visual status indication",
        "Remote monitoring capability",
        "Supports high impulse currents",
        "SEC (Safe Energy Control) Technology",
        "Suitable for industrial and telecom systems",
      ],
      advantages: [
        "Long service life",
        "Handles extreme surge conditions",
        "Compact DIN rail design",
        "Easy replacement",
        "Reliable system protection",
      ],
      specs: `
        <tr><td>Voltage</td><td>240V AC</td></tr>
        <tr><td>Impulse Current</td><td>25 kA</td></tr>
        <tr><td>Technology</td><td>SEC</td></tr>
        `,
    },
    psu_ups: {
      title: "Power Supply & UPS Module",
      desc: "Phoenix Contact power supply and UPS modules ensure uninterrupted and stable power delivery for industrial systems. These solutions are designed to maintain continuous operation even during power failures, preventing data loss and system downtime. With intelligent battery management, robust design, and high efficiency, they are ideal for automation, control panels, and critical infrastructure applications.",
      img: "images/power_supply.webp",
      features: [
        "Integrated UPS functionality",
        "Battery management system",
        "Wide input voltage range",
        "DIN rail mounting",
        "Status indication LEDs",
        "Compact industrial design",
      ],
      advantages: [
        "Ensures uninterrupted operation",
        "Protects against power failures",
        "High efficiency and reliability",
        "Easy installation and maintenance",
        "Long operational life",
      ],
      specs: `
        <tr><td>Input Voltage</td><td>24V DC</td></tr>
        <tr><td>Output Voltage</td><td>24V DC</td></tr>
        <tr><td>Mounting</td><td>DIN Rail</td></tr>
        `,
    },

    relay: {
      title: "Relay & Isolation Modules",
      desc: "Relay and isolation modules are used for safe switching and signal isolation in industrial automation. They ensure protection of control systems from high voltage spikes and noise.",
      img: "images/realy.jpg",
      features: [
        "Electromechanical and solid-state relays",
        "Signal isolation",
        "LED status indicators",
        "Compact design",
        "Plug-in modules",
      ],
      advantages: [
        "Improved safety",
        "Long switching life",
        "Easy maintenance",
        "Noise protection",
        "Reliable operation",
      ],
      specs: `
    <tr><td>Voltage</td><td>230V AC</td></tr>
    <tr><td>Type</td><td>Solid State</td></tr>
    <tr><td>Mounting</td><td>DIN Rail</td></tr>
    `,
    },

    network: {
      title: "Ethernet Network Components",
      desc: "Industrial Ethernet components from Phoenix Contact provide secure and fast communication between devices in automation systems.",
      img: "images/Ethernet_Switches.jpg",
      features: [
        "Managed and unmanaged switches",
        "High-speed data transfer",
        "Redundancy support",
        "Industrial-grade design",
        "Secure communication",
      ],
      advantages: [
        "Reliable networking",
        "Fast communication",
        "High durability",
        "Easy integration",
        "Scalable systems",
      ],
      specs: `
    <tr><td>Speed</td><td>1 Gbps</td></tr>
    <tr><td>Ports</td><td>8/16/24</td></tr>
    <tr><td>Protocol</td><td>Ethernet/IP</td></tr>
    `,
    },

    io: {
      title: "Digital & Analog I/O Modules",
      desc: "These modules are used for input and output signal processing in automation systems, supporting both digital and analog signals.",
      img: "images/Digital_IO_Module.jpg",
      features: [
        "Digital and analog inputs",
        "High accuracy",
        "Compact design",
        "Fast signal processing",
        "Modular expansion",
      ],
      advantages: [
        "Flexible usage",
        "Accurate data",
        "Scalable system",
        "Reliable performance",
        "Easy configuration",
      ],
      specs: `
    <tr><td>Channels</td><td>8/16</td></tr>
    <tr><td>Signal Type</td><td>Digital/Analog</td></tr>
    <tr><td>Response Time</td><td>Fast</td></tr>
    `,
    },

    controller: {
      title: "Programmable E-Mobility Charging Controller",
      desc: "Phoenix Contact controllers provide intelligent control and monitoring for complex charging infrastructures. These programmable controllers are designed for e-mobility applications, enabling efficient communication, energy management, and system integration. Built for reliability and flexibility, they support modern automation and smart grid requirements.",
      img: "images/controller.jpeg",
      features: [
        "Programmable control logic",
        "Supports complex AC/DC charging systems",
        "Integrated communication interfaces",
        "Real-time monitoring capability",
        "Compact and modular design",
        "Compatible with industrial protocols",
      ],
      advantages: [
        "Optimized charging performance",
        "Flexible system integration",
        "High reliability in industrial environments",
        "Scalable for different applications",
        "Improves energy efficiency",
      ],
      specs: `
    <tr><td>Application</td><td>E-Mobility Charging</td></tr>
    <tr><td>Control Type</td><td>Programmable</td></tr>
    <tr><td>Communication</td><td>Industrial Protocol Support</td></tr>
    `,
    },

    hmi: {
      title: "HMI & Industrial Computers",
      desc: "Human Machine Interfaces (HMI) and industrial PCs provide visualization and control of industrial processes with advanced computing capabilities.",
      img: "images/HMI.png",
      features: [
        "Touchscreen interface",
        "Real-time monitoring",
        "Industrial-grade hardware",
        "High processing power",
        "Remote access support",
      ],
      advantages: [
        "User-friendly control",
        "Better visualization",
        "Fast processing",
        "Improved productivity",
        "Reliable operation",
      ],
      specs: `
    <tr><td>Display</td><td>10-15 inch</td></tr>
    <tr><td>Processor</td><td>Industrial CPU</td></tr>
    <tr><td>OS</td><td>Windows/Linux</td></tr>
    `,
    },
  };

  // ================================
  // LOAD DATA
  // ================================
  if (product && data[product]) {
    const p = data[product];

    if (title) title.innerText = p.title;
    if (desc) desc.innerText = p.desc;
    if (img) img.src = p.img;

    if (featuresBox) {
      featuresBox.innerHTML = `<h2>Features</h2><ul>${p.features.map((f) => `<li>${f}</li>`).join("")}</ul>`;
    }

    if (advantagesBox) {
      advantagesBox.innerHTML = `<h2>Advantages</h2><ul>${p.advantages.map((a) => `<li>${a}</li>`).join("")}</ul>`;
    }

    if (specsBox) {
      specsBox.innerHTML = `<h2>Technical Specs</h2><table>${p.specs}</table>`;
    }
  } else {
    if (title) title.innerText = "Product Not Found";
  }

  // ================================
  // SCROLL ANIMATION (MAIN FIX)
  // ================================
  const elements = document.querySelectorAll(
    ".details-section, .animate-left, .animate-right, .animate-bottom, .box",
  );

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("show");
        } else {
          entry.target.classList.remove("show"); // repeat animation
        }
      });
    },
    {
      threshold: 0.2,
    },
  );

  elements.forEach((el) => observer.observe(el));
});

document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menu-toggle");
  const navLinks = document.getElementById("nav-links");
  const closeMenu = document.getElementById("close-menu");

  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      navLinks.classList.add("active");
    });
  }

  if (closeMenu && navLinks) {
    closeMenu.addEventListener("click", () => {
      navLinks.classList.remove("active");
    });
  }

  const aboutToggle = document.querySelector(".mobile-dropdown-toggle");
  const aboutDropdown = document.querySelector(".about-dropdown");

  if (aboutToggle && aboutDropdown) {
    aboutToggle.addEventListener("click", () => {
      aboutDropdown.classList.toggle("show");
    });
  }
});
