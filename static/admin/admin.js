////////  sidebar dropdown function ///
function toggleSidebarDropdown(menuId) {
  const menu = document.getElementById(menuId);

  menu.classList.toggle("active");
}


function showSection(sectionId) {
  const sections = document.querySelectorAll(".section");
  sections.forEach(section => {
    section.classList.remove("active");
  });

  document.getElementById(sectionId).classList.add("active");
}


window.onload = function () {
    let hash = window.location.hash;

    if (hash) {
        let sectionId = hash.replace("#", "");
        showSection(sectionId);
    } else {
        showSection('dashboard');
    }
};


function toggleSidebar(){
    document.querySelector(".sidebar").classList.toggle("show");
}

document.querySelectorAll(".sidebar li").forEach(item => {
    item.addEventListener("click", () => {
        if(window.innerWidth <= 768){
            document.querySelector(".sidebar").classList.remove("show");
        }
    });
});



const today = new Date();

const options = {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric'
};

document.getElementById("today-date").innerHTML =
"📅 " + today.toLocaleDateString("en-IN", options);

document.addEventListener("DOMContentLoaded", function () {

    const nameInput = document.getElementById("client_name");
    const codeInput = document.getElementById("client_code");
    const clientIdInput = document.getElementById("client_id");
    const addBtn = document.querySelector(".add-button");
    const updateBtn = document.getElementById("update-btn");

    // =========================
    // CHECK DUPLICATE NAME
    // =========================
    function checkClientName() {

        let clientId = clientIdInput.value;
        let name = nameInput.value.trim();

        if (name === "") return;

        fetch("/check_client", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body:
                "client_name=" + encodeURIComponent(name) +
                "&client_id=" + encodeURIComponent(clientId)
        })
        .then(response => response.json())
        .then(data => {

            if (data.name_exists) {
                nameInput.setCustomValidity("Client name already exists!");
                nameInput.reportValidity();
            } else {
                nameInput.setCustomValidity("");
            }

        });
    }

    nameInput.addEventListener("blur", checkClientName);

    // =========================
    // AUTOFILL BY CLIENT CODE
    // =========================
    codeInput.addEventListener("blur", function() {

        let code = this.value.trim();
        if (code === "") return;

        fetch("/get_client_by_code", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: "client_code=" + encodeURIComponent(code)
        })
        .then(response => response.json())
        .then(data => {

            if (data.exists) {

                // Autofill
                clientIdInput.value = data.client_id;
                nameInput.value = data.client_name;
                document.getElementById("email").value = data.email;
                document.getElementById("phone").value = data.phone;
                document.getElementById("city").value = data.city;

                // Switch to UPDATE mode
                addBtn.style.display = "none";
                updateBtn.style.display = "inline-block";

                // 🔥 VERY IMPORTANT:
                nameInput.setCustomValidity("");

            } else {

                // Reset to INSERT mode
                clientIdInput.value = "";
                addBtn.style.display = "inline-block";
                updateBtn.style.display = "none";

                nameInput.setCustomValidity("");
            }

        });

    });

});



function checkEmployeeCode(){

    let code = document.getElementById("employee_code").value;

    fetch("/get_employee_by_code",{
        method:"POST",
        headers:{
            "Content-Type":"application/x-www-form-urlencoded"
        },
        body:"employee_code="+code
    })
    .then(response=>response.json())
    .then(data=>{

        if(data.exists){

            document.getElementById("employee_id").value = data.employee_id;
            document.getElementById("first_name").value = data.first_name;
            document.getElementById("last_name").value = data.last_name;
            document.getElementById("dob").value = data.dob;
            document.getElementById("doj").value = data.doj;
            document.getElementById("grade_id").value = data.grade_id;
            document.getElementById("location_id").value = data.location_id;
            document.getElementById("project_id_emp").value = data.project_id;
            document.getElementById("phone_emp").value = data.phone;
            document.getElementById("aadhar_number").value = data.aadhar_number;
            document.getElementById("pan_number").value = data.pan_number;

            document.getElementById("addBtn").style.display="none";
            document.getElementById("updateBtn").style.display="inline";

        }
    })
}



// ============================
// COMMON VALIDATION FUNCTIONS
// ============================

function validateEmailField(inputId) {
    let input = document.getElementById(inputId);
    let value = input.value.trim();
    let errorSpan = document.getElementById(inputId + "-error");

    let pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (value !== "" && !pattern.test(value)) {
        input.classList.add("input-error");
        if (errorSpan) errorSpan.innerText = "Invalid email format";
    } else {
        input.classList.remove("input-error");
        if (errorSpan) errorSpan.innerText = "";
    }
}

function validatePhoneField(inputId) {
    let input = document.getElementById(inputId);
    let value = input.value.trim();
    let errorSpan = document.getElementById(inputId + "-error");

    // Task 2: Allow 0-9 starting digit, 10-15 total digits
    let pattern = /^[0-9]\d{9,14}$/;

    if (value !== "" && !pattern.test(value)) {
        input.classList.add("input-error");
        if (errorSpan) errorSpan.innerText = "Enter valid 10-15 digit number";
    } else {
        input.classList.remove("input-error");
        if (errorSpan) errorSpan.innerText = "";
    }
}

function validateNameField(inputId) {
    let input = document.getElementById(inputId);
    let value = input.value.trim();
    let errorSpan = document.getElementById(inputId + "-error");

    // should not start with number
    let pattern = /^[A-Za-z][A-Za-z\s]*$/;

    if (value !== "" && !pattern.test(value)) {
        input.classList.add("input-error");
        if (errorSpan) errorSpan.innerText = "Must start with a letter";
    } else {
        input.classList.remove("input-error");
        if (errorSpan) errorSpan.innerText = "";
    }
}



const startDateInput = document.getElementById("start_date");
const endDateInput = document.getElementById("end_date");

function validateProjectDates() {

    let start = new Date(startDateInput.value);
    let end = new Date(endDateInput.value);

    if (startDateInput.value && endDateInput.value) {

        if (end < start) {
            endDateInput.setCustomValidity("End date cannot be before start date");
        } else {
            endDateInput.setCustomValidity("");
        }

        endDateInput.reportValidity();
    }
}

startDateInput.addEventListener("change", validateProjectDates);
endDateInput.addEventListener("change", validateProjectDates);



const dobInput = document.getElementById("dob");
const dojInput = document.getElementById("doj");

function validateEmployeeDates() {

    let dob = new Date(dobInput.value);
    let doj = new Date(dojInput.value);
    let today = new Date();

    // ✅ Future DOB check
    if (dobInput.value) {
        if (dob > today) {
            dobInput.setCustomValidity("DOB cannot be in the future");
        } else {
            dobInput.setCustomValidity("");
        }
        dobInput.reportValidity();
    }

    // ✅ DOJ after DOB check
    if (dobInput.value && dojInput.value) {

        if (doj < dob) {
            dojInput.setCustomValidity("Joining date cannot be before DOB");
        } else {
            dojInput.setCustomValidity("");
        }

        dojInput.reportValidity();
    }


}

dobInput.addEventListener("change", validateEmployeeDates);
dojInput.addEventListener("change", validateEmployeeDates);




function openTab(evt, tabName) {

    // Hide all tab contents
    let contents = document.getElementsByClassName("tab-content");
    for (let i = 0; i < contents.length; i++) {
        contents[i].classList.remove("active");
    }

    // Remove active from all buttons
    let buttons = document.getElementsByClassName("tab-btn");
    for (let i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove("active");
    }

    // Show selected tab
    document.getElementById(tabName).classList.add("active");
    evt.currentTarget.classList.add("active");
}


// nav bar js
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

// function exportAttendanceExcel() {
//     const month = document.getElementById("month").value;
//     const year = document.getElementById("year").value;
//     const emp_id = document.getElementById("emp_id").value;
//     const department = document.getElementById("department").value;

//     let url = `/export/attendance?month=${month}&year=${year}`;
//     if (emp_id) url += `&emp_id=${emp_id}`;
//     if (department) url += `&department=${department}`;

//     window.location.href = url;
// }



// =============================
// SERVICE EDIT
// =============================
function fillService(id, title, description) {
  document.getElementById("service_id").value = id;
  document.getElementById("service_title").value = title;
  document.getElementById("service_description").value = description;

  window.scrollTo({
    top: document.getElementById("service").offsetTop,
    behavior: "smooth",
  });
}

function fillServiceDetail(id, longDescription, image) {
  document.getElementById("service_detail_id").value = id;

  document.getElementById("detail_long_description").value = longDescription;

  // Scroll to the form
  window.scrollTo({
    top: document.getElementById("detail_service_id").offsetTop - 100,
    behavior: "smooth",
  });
}

function fillScope(id, title, description) {
  console.log(document.getElementById("scope_id"));
  console.log(document.getElementById("scope_title"));
  console.log(document.getElementById("scope_description"));

  document.getElementById("scope_id").value = id;
  document.getElementById("scope_title").value = title;
  document.getElementById("scope_description").value = description;
}

function fillJourney(id, year, title, description) {
  document.getElementById("journey_id").value = id;
  document.getElementById("journey_year").value = year;
  document.getElementById("journey_title").value = title;
  document.getElementById("journey_description").value = description;

  // Show Update button and hide Add button
  document.querySelector('button[value="INSERT"]').style.display = "none";
  document.querySelector('button[value="UPDATE"]').style.display =
    "inline-block";

  // Scroll to Journey form
  window.scrollTo({
    top: document.querySelector('input[id="journey_id"]').closest(".card")
      .offsetTop,
    behavior: "smooth",
  });
}

function fillNews(title, desc, img) {
  openNews({
    dataset: {
      title: title,
      desc: desc,
      img: img,
    },
  });
}

function editFAQ(id, category, question, answer) {
  // Fill form
  document.getElementById("faq_id").value = id;
  document.getElementById("category_id").value = category;
  document.getElementById("question").value = question;
  document.getElementById("answer").value = answer;

  // Hide Add button
  document.getElementById("addBtn").style.display = "none";

  // Show Update button
  document.getElementById("updateBtn").style.display = "inline-block";

  // Scroll to form
  document.getElementById("faq").scrollIntoView({
    behavior: "smooth",
  });
}

function updateFAQ() {
  let id = document.getElementById("faq_id").value;

  document.getElementById("faqForm").action = "/update_faq/" + id;
  document.getElementById("faqForm").submit();
}

const heroForm = document.getElementById("heroForm");

if (heroForm) {
  heroForm.addEventListener("submit", saveHero);
}
async function saveHero(e) {
  e.preventDefault();

  const formData = new FormData();

  formData.append("title", document.getElementById("title").value);

  formData.append("description", document.getElementById("description").value);

  formData.append("image", document.getElementById("image").files[0]);

  await fetch("/admin/about/hero/add", {
    method: "POST",

    body: formData,
  });

  heroForm.reset();

  loadHero();
}
async function loadHero() {
  const response = await fetch("/admin/about/hero/list");

  const data = await response.json();

  let html = "";

  data.forEach((hero) => {
    html += `

<tr>

<td>${hero.id}</td>

<td>

<img
src="/static/about/images_about/${hero.image}"
width="90">

</td>

<td>${hero.title}</td>

<td>${hero.description.substring(0, 60)}...</td>

<td>

${hero.status ? "Active" : "Inactive"}

</td>

<td>

<button onclick="editHero(${hero.id})">

Edit

</button>

<button onclick="deleteHero(${hero.id})">

Delete

</button>

</td>

</tr>

`;
  });

  const table = document.getElementById("heroTable");

  if (table) {
    table.innerHTML = html;
  }
}
async function deleteHero(id) {
  if (confirm("Delete Hero Section?")) {
    await fetch("/admin/about/hero/delete/" + id);

    loadHero();
  }
}
function editHero(id) {
  // Will add later
}
if (document.getElementById("heroTable")) {
  loadHero();
}
