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

    console.log("onload fired");

    try {

        let hash = window.location.hash;

        if (hash) {
            let sectionId = hash.replace("#", "");
            showSection(sectionId);
        } else {
            showSection('dashboard');
        }

        // ============================
        // Year Dropdown
        // ============================
        const yearSelect = document.getElementById("year");

        console.log("Year Select:", yearSelect);

        if (yearSelect) {

            const currentYear = new Date().getFullYear();

            yearSelect.innerHTML = "";

            for (let y = currentYear; y >= currentYear - 100; y--) {

                yearSelect.innerHTML +=
                    `<option value="${y}" ${y === currentYear ? "selected" : ""}>${y}</option>`;
            }

            console.log("Year Dropdown Loaded");
        } else {
            console.log("Year dropdown not found.");
        }

        // ============================
        // Current Month
        // ============================
        const monthSelect = document.getElementById("month");

        if (monthSelect) {
            monthSelect.value = (new Date().getMonth() + 1).toString();
        }

        // ============================
        // Load Departments
        // ============================
        if (document.getElementById("department")) {
            loadDepartments();
        }

        console.log("Month and Department Loaded");

        // Default report tab
        if(document.getElementById("monthlyReportCard")){
            switchReportTab("monthly");
        }

    } catch (err) {
        console.error("Window onload error:", err);
    }
};

function switchReportTab(type){


    const monthly =
    document.getElementById("monthlyReportCard");


    const detail =
    document.getElementById("detailedReportCard");


    const monthlyBtn =
    document.getElementById("monthlyTab");


    const detailBtn =
    document.getElementById("detailTab");



    if(type==="monthly"){


        if(monthly)
            monthly.style.display="block";


        if(detail)
            detail.style.display="none";


        if(monthlyBtn)
            monthlyBtn.classList.add("active");


        if(detailBtn)
            detailBtn.classList.remove("active");


    }

    else{


        if(monthly)
            monthly.style.display="none";


        if(detail)
            detail.style.display="block";


        if(detailBtn)
            detailBtn.classList.add("active");


        if(monthlyBtn)
            monthlyBtn.classList.remove("active");


    }

}


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

async function loadReport(){


    // Open Monthly Matrix Tab
    if(typeof switchReportTab === "function"){
        switchReportTab("monthly");
    }


    const monthlyCard = document.getElementById("monthlyReportCard");
    const legend = document.getElementById("statusLegend");
    const detailedCard = document.getElementById("detailedReportCard");


    if(monthlyCard)
        monthlyCard.style.display="block";


    if(legend)
        legend.style.display="block";


    if(detailedCard)
        detailedCard.style.display="none";

    // Hide placeholder after clicking Generate Report
    const placeholder = document.getElementById("reportPlaceholder");
    if (placeholder) {
        placeholder.style.display = "none";
    }

    let month = document.getElementById("month").value;
    let year = document.getElementById("year").value;
    let employeeInput = document.getElementById("report_employee_id");

    let employee_id = "";

    if(employeeInput){
        employee_id = employeeInput.value.trim();
    }

    console.log("EMPLOYEE INPUT VALUE:", employee_id);

    if(employee_id !== ""){
        employee_id = Number(employee_id);
    }
    else{
        employee_id = null;
    }
    let department = document.getElementById("department").value;

    let url = `/api/monthly_matrix_report?month=${month}&year=${year}`;

    if (employee_id !== null && !isNaN(employee_id)) {
        url += `&employee_id=${employee_id}`;
    }
    if(department){
        url += `&department=${department}`;
    }
    console.log("FINAL URL:", url);
    const res = await fetch(url);

    const result = await res.json();
    console.log("API RESULT:", result);


    let table = document.getElementById("reportTable");

    table.innerHTML = "";

    const monthName =
        document.getElementById("month")
        .options[document.getElementById("month").selectedIndex].text;

    // =========================================
    // CURRENT DATE/TIME
    // =========================================

    const now = new Date();

    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;
    const currentDay = now.getDate();
    const currentHour = now.getHours();

    // =========================================
    // REPORT TITLE
    // =========================================

    let html = `

    <tr>
        <th colspan="${result.total_days + 2}" class="main-header">
            REPORT FOR : ${monthName.toUpperCase()} ${year}
        </th>
    </tr>

    `;

    // =========================================
    // DAY NAME HEADER ROW
    // =========================================

    html += `

    <tr>

        <th rowspan="2" class="code-cell" style="width:70px">
            EMP ID
        </th>

        <th rowspan="2" class="name-section" style="width:180px">
            EMPLOYEE DETAILS
        </th>
    `;

    for(let i = 1; i <= result.total_days; i++){

        const date = new Date(year, month - 1, i);

        const dayName = date.toLocaleDateString(
            'en-US',
            {
                weekday:'short'
            }
        );

        let cls = "";

        if(dayName === "Sun"){
            cls = "sunday";
        }
        else if(dayName === "Sat"){
            cls = "saturday";
        }

        html += `
            <th class="${cls}">
                ${dayName}
            </th>
        `;
    }

    html += `</tr>`;

    // =========================================
    // DATE HEADER ROW
    // =========================================

    html += `<tr>`;

    for(let i = 1; i <= result.total_days; i++){

        html += `
            <th>
                ${i}
            </th>
        `;
    }

    html += `</tr>`;

    // =========================================
    // EMPLOYEE LOOP
    // =========================================

    result.data.forEach(emp => {

        html += `

        <tr>

            <td class="code-cell">
                ${emp.employee_id} 
            </td>

            <td class="name-section">

                <div class="emp-name">
                    ${emp.employee_name}
                </div>

                <div class="emp-role">
                    ${emp.role || "-"}
                </div>

                <div class="emp-dept">
                    ${emp.department || "-"}
                </div>

            </td>
        `;

        // =====================================
        // DAILY STATUS CELLS
        // =====================================

        for(let i = 1; i <= result.total_days; i++){

            const key = String(i).padStart(2,'0');

            let finalVal = emp.attendance[key];

            // =================================
            // FUTURE YEAR/MONTH
            // =================================

            if(
                result.year > currentYear ||
                (
                    result.year == currentYear &&
                    result.month > currentMonth
                )
            ){

                finalVal = "-";
            }

            // =================================
            // CURRENT MONTH CONDITIONS
            // =================================

            else if(
                result.year == currentYear &&
                result.month == currentMonth
            ){

                // Only hide future dates
                if(i > currentDay){

                    finalVal = "-";
                }
            }

            // =================================
            // EMPTY SAFETY
            // =================================

            // default handling
            if(finalVal == null || finalVal == undefined || finalVal == ""){
                finalVal = "-";
            }

            let statusClass = "";
            if (finalVal === "P") statusClass = "P";
            else if (finalVal === "A") statusClass = "A";
            else if (finalVal === "HD") statusClass = "HD";
            else if (finalVal === "H") statusClass = "H";
            else if (finalVal === "L") statusClass = "L";
            else if (finalVal === "WO") statusClass = "WO";

            // then build HTML
            html += `
            <td class="status-cell ${statusClass}">
                ${finalVal}
            </td>
            `;
        }

        html += `
        </tr>
        `;

        // =====================================
        // REPORT TOTALS ROW
        // =====================================

        html += `

        <tr class="totals-row">

            <td colspan="2" class="report-total-title">
                REPORT TOTALS
            </td>

            <td colspan="${result.total_days}" class="totals-data">

                <span>
                    Present: <b>${emp.summary.present}</b>
                </span>

                <span>
                    Absent: <b>${emp.summary.absent}</b>
                </span>

                <span>
                    Half Day: <b>${emp.summary.half_day}</b>
                </span>

                <span>
                    Leave: <b>${emp.summary.leave}</b>
                </span>

                <span>
                    Holiday: <b>${emp.summary.holiday}</b>
                </span>

                <span>
                    WO: <b>${emp.summary.weekly_off}</b>
                </span>

            </td>

        </tr>
        `;
    });

    table.innerHTML = html;
}
// FORCE GLOBAL ACCESS HERE:
window.loadReport = loadReport;

async function loadDetailedReport(){


    // Open Detailed Tab
    if(typeof switchReportTab === "function"){
        switchReportTab("detail");
    }


    let empField = document.getElementById("report_employee_id");
    let deptField = document.getElementById("department");

    // Reset borders
    empField.style.border = "";
    deptField.style.border = "";

    if(!empField.value){
        empField.style.border = "2px solid red";
        alert("Employee ID is mandatory for Detailed Report");
        return;
    }

    if(!deptField.value){
        deptField.style.border = "2px solid red";
        alert("Department is mandatory for Detailed Report");
        return;
    }


    const monthlyCard = document.getElementById("monthlyReportCard");
    const legend = document.getElementById("statusLegend");
    const detailedCard = document.getElementById("detailedReportCard");

    if (monthlyCard) monthlyCard.style.display = "none";
    if (legend) legend.style.display = "none";
    if (detailedCard) detailedCard.style.display = "block";


    let month = document.getElementById("month").value;
    let year = document.getElementById("year").value;
    let employee_id = empField.value;
    let department = deptField.value;


    let url =
    `/api/monthly_detailed_report?month=${month}&year=${year}&employee_id=${employee_id}`;


    if(department){
        url += `&department=${department}`;
    }

    const res = await fetch(url);

    const result = await res.json();

    if(result.data.length > 0){

        let emp = result.data[0];

        document.getElementById("employeeInfoBar").innerHTML = `
            <div style="
                padding:12px 20px;
                background:#f8fafc;
                border-bottom:1px solid #ddd;
                font-size:15px;
                font-weight:bold;
            ">
                Employee :
                ${emp.employee_name}

                &nbsp;&nbsp;&nbsp; |

                Employee ID :
                ${emp.employee_id}

                &nbsp;&nbsp;&nbsp; |

                Department :
                ${emp.department}
            </div>
        `;
    }

    document.getElementById("detailedReportCard").style.display =
    "block";

    let html = `
    <tr>
        <th>Date</th>
        <th>Check In</th>
        <th>Check Out</th>
        <th>Work Hours</th>
        <th>Arrival</th>
        <th>Checkout Type</th>
        <th>Final Status</th>
    </tr>
    `;

    let rowsFound = false;
    let present = 0;
    let absent = 0;
    let halfDay = 0;
    let holiday = 0;
    let leave = 0;
    let weeklyOff = 0;

    result.data.forEach(emp => {

        emp.records.forEach(row => {

            rowsFound = true;

            if(row.status === "Present"){
                present++;
            }
            else if(row.status === "Absent"){
                absent++;
            }
            else if(row.status === "Half Day"){
                halfDay++;
            }
            else if(row.status === "Holiday"){
                holiday++;
            }
            else if(row.status === "Leave"){
                leave++;
            }
            else if(row.status === "Weekly Off"){
                weeklyOff++;
            }

            let arrivalClass =
                row.arrival === "Late"
                ? "arrival-late"
                : "arrival-ontime";

            let checkoutClass =
                row.checkout_type === "Auto"
                ? "checkout-auto"
                : "checkout-manual";

            let statusClass = "";

            if(row.status === "Present"){
                statusClass = "status-present";
            }
            else if(row.status === "Half Day"){
                statusClass = "status-halfday";
            }
            else if(row.status === "Absent"){
                statusClass = "status-absent";
            }
            else if(row.status === "Leave"){
                statusClass = "status-leave";
            }
            else if(row.status === "Holiday"){
                statusClass = "status-holiday";
            }
            else if(row.status === "Weekly Off"){
                statusClass = "status-weekoff";
            }

            let remarks = "-";

            if(row.status === "Absent"){
                remarks = "No Attendance";
            }

            if(row.status === "Leave"){
                remarks = "Approved Leave";
            }

            if(row.status === "Holiday"){
                remarks = "Company Holiday";
            }

            if(row.status === "Weekly Off"){
                remarks = "Weekly Off";
            }

            // ==========================================
            // HOLIDAY / LEAVE / WEEKLY OFF FULL ROW
            // ==========================================

            if(
                row.status === "Holiday" ||
                row.status === "Leave" ||
                row.status === "Weekly Off"
            ){

                let rowClass = "";

                if(row.status === "Holiday"){
                    rowClass = "holiday-row";
                }
                else if(row.status === "Leave"){
                    rowClass = "leave-row";
                }
                else{
                    rowClass = "weeklyoff-row";
                }

                html += `
                <tr class="${rowClass}">

                    <td>${row.date}</td>

                    <td colspan="6" class="special-day">
                        ${row.status}
                    </td>

                </tr>
                `;
            }
            else{

                html += `
                <tr>

                    <td>${row.date}</td>

                    <td>${row.check_in || "-"}</td>

                    <td>${row.check_out || "-"}</td>

                    <td>${row.hours || "-"}</td>

                    <td class="${arrivalClass}">
                        ${row.arrival || "-"}
                    </td>

                    <td class="${checkoutClass}">
                        ${row.checkout_type || "-"}
                    </td>

                    <td class="${statusClass}">
                        ${row.status}
                    </td>

                </tr>
                `;
            }
        });

    });

    if(!rowsFound){

        html += `
        <tr>
            <td colspan="9">
                No attendance records found for selected filters
            </td>
        </tr>
        `;
    }

        html += `
        <tr class="totals-footer">
            <td colspan="9">

                Present : ${present}
                &nbsp;&nbsp;&nbsp;|

                Absent : ${absent}
                &nbsp;&nbsp;&nbsp;|

                Half Day : ${halfDay}
                &nbsp;&nbsp;&nbsp;|

                Leave : ${leave}
                &nbsp;&nbsp;&nbsp;|

                Holiday : ${holiday}
                &nbsp;&nbsp;&nbsp;|

                Weekly Off : ${weeklyOff}

            </td>
        </tr>
        `;

    document.getElementById("detailedReportTable").innerHTML =
    html;
}
// FORCE GLOBAL ACCESS HERE:
window.loadDetailedReport = loadDetailedReport;

function downloadPDF() {

    let monthEl = document.getElementById("month");
    let yearEl = document.getElementById("year");
    let empEl = document.getElementById("report_employee_id");
    let deptEl = document.getElementById("department");

    if (!monthEl || !yearEl) {
        console.error("Month/Year elements missing");
        return;
    }

    let month = monthEl.value;
    let year = yearEl.value;

    let employee_id = empEl ? empEl.value : "";
    if (employee_id) {
        employee_id = parseInt(employee_id);
    }

    let department = deptEl ? deptEl.value : "";

    // ===============================
    // SAFE ELEMENT CHECKS
    // ===============================
    let detailedCard = document.getElementById("detailedReportCard");
    let monthlyCard = document.getElementById("monthlyReportCard");

    let isDetailedVisible =
        detailedCard && getComputedStyle(detailedCard).display !== "none";

    let isMonthlyVisible =
        monthlyCard && getComputedStyle(monthlyCard).display !== "none";

    // ===============================
    // DECIDE API
    // ===============================
    let url = "";

    if (isDetailedVisible) {

        url =
        `/api/download_detailed_report_pdf?month=${month}&year=${year}`;

    }
    else {

        url =
        `/api/download_monthly_report_pdf?month=${month}&year=${year}`;

    }

    // ===============================
    // ADD FILTERS
    // ===============================
    if (employee_id) {
        url += `&employee_id=${employee_id}`;
    }

    if (department) {
        url += `&department=${department}`;
    }

    console.log("PDF URL:", url);
    console.log("Detailed Visible:", isDetailedVisible);
    console.log("Monthly Visible:", isMonthlyVisible);
    

    // ===============================
    // DOWNLOAD
    // ===============================
    window.open(url, "_blank");
}

async function loadDepartments(){

    const res = await fetch("/api/get_departments");

    const data = await res.json();

    let deptSelect = document.getElementById("department");

    deptSelect.innerHTML =
        `<option value="">All Departments</option>`;

    data.forEach(d => {

        deptSelect.innerHTML += `
            <option value="${d.department_name}">
                ${d.department_name}
            </option>
        `;
    });
}