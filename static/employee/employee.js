/* ================= SHOW SECTION ================= */
function showSection(section){

  const welcome = document.querySelector(".welcome");
  const profile = document.querySelector(".profile-section");
  const content = document.querySelector(".content-section");
  const main = document.querySelector(".main");
  const tabs = document.querySelectorAll(".tab");

  // Hide welcome
  welcome.classList.add("hide");

  // Activate layout
  main.classList.add("active-layout");

  // Move profile left
  profile.classList.add("profile-left");

  // Show content container
  content.style.display = "block";

  // Hide all tabs
  tabs.forEach(tab => tab.style.display = "none");

  // Show selected tab
  document.getElementById(section).style.display = "block";

  // Animate content
  content.classList.remove("active");
  void content.offsetWidth;
  content.classList.add("active");

  // Highlight active button
  setActiveButton(section);
}

/* ================= ACTIVE BUTTON ================= */
function setActiveButton(section){
  const buttons = document.querySelectorAll(".sidebar button");

  buttons.forEach(btn => btn.classList.remove("active"));

  if(section === "profile") buttons[0].classList.add("active");
  if(section === "salary") buttons[1].classList.add("active");
  if(section === "tds") buttons[2].classList.add("active");
  if(section === "resume") buttons[3].classList.add("active");
  if(section === "leave") buttons[4].classList.add("active");
}

/* ================= SALARY ================= */
function generateSlip(){
  alert("✅ Salary Slip Generated Successfully!");
}

/* ================= RESUME ================= */
/* DOWNLOAD RESUME */
// function downloadResume(){
// let loader = document.getElementById("resumeLoader");
// loader.style.display = "block";

// setTimeout(()=>{
// loader.style.display = "none";
// alert("Resume Downloaded Successfully!");
// },2000);
// }

function showFileName(){

    let file =
        document.getElementById("resumeFile");

    let text =
        document.getElementById("fileName");

    if(file.files.length>0){

        text.innerHTML=file.files[0].name;

    }
}

/* ================= LOGOUT ================= */
function downloadResume(){

    window.location.href="/download_resume";

}
/* ================= WORKING DAYS CALCULATOR ================= */
function calcDays() {
  const sd = document.getElementById('start_date').value;
  const ed = document.getElementById('end_date').value;
  const badge = document.getElementById('daysBadge');

  if (!sd || !ed) { badge.textContent = '— days'; return; }

  const start = new Date(sd);
  const end   = new Date(ed);

  if (end < start) { badge.textContent = '❌ Invalid'; badge.style.color = 'red'; return; }

  let count = 0;
  let cur = new Date(start);
  while (cur <= end) {
    const day = cur.getDay();
    if (day !== 0 && day !== 6) count++; // skip Sat & Sun
    cur.setDate(cur.getDate() + 1);
  }

  badge.style.color = '#4f5bd5';
  badge.textContent = count + (count === 1 ? ' working day' : ' working days');
}

/* ================= PROFILE PHOTO PREVIEW & UPLOAD ================= */
function previewAndUpload(input) {
  if (input.files && input.files[0]) {
    const file = input.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
      document.getElementById('profileImg').src = e.target.result;
    };
    reader.readAsDataURL(file);
    document.getElementById('photoForm').submit();
  }
}


// =====================================
// LEAVE MANAGEMENT
// =====================================

document.addEventListener("DOMContentLoaded", () => {

    loadDashboard();
    loadRequests();

    // AUTO DAYS
    document.getElementById("from")
    ?.addEventListener("change", calculateDays);

    document.getElementById("to")
    ?.addEventListener("change", calculateDays);

    document.getElementById("leaveType")
    ?.addEventListener("change", calculateDays);

});

// MODAL
function openModal(){
    document.getElementById("modal")
    .classList.add("show");
}

function closeModal(){

    document.getElementById("modal")
    .classList.remove("show");

    document.getElementById("from").value = "";
    document.getElementById("to").value = "";
    document.getElementById("days").value = "";
    document.getElementById("reason").value = "";

}

// CALCULATE DAYS
function calculateDays(){

    let from =
    document.getElementById("from").value;

    let to =
    document.getElementById("to").value;

    let leaveType =
    document.getElementById("leaveType").value;

    if(leaveType == "Half Day" && from){

        document.getElementById("to").value = from;

        document.getElementById("days").value = 0.5;

        return;
    }

    if(from && to){

        let start = new Date(from);
        let end = new Date(to);

        let diff = end - start;

        let days =
        diff / (1000 * 60 * 60 * 24) + 1;

        if(days > 0){
            document.getElementById("days").value = days;
        }
    }

}

// LOAD DASHBOARD
function loadDashboard(){

    fetch('/api/leave/dashboard')

    .then(res => res.json())

    .then(data => {

        document.getElementById("available").innerText =
        data.available;

        document.getElementById("pending").innerText =
        data.pending;

        document.getElementById("approved").innerText =
        data.approved;

    });

}

// APPLY LEAVE
async function applyLeave(){

    let from =
    document.getElementById("from").value;

    let to =
    document.getElementById("to").value;

    let days =
    document.getElementById("days").value;

    let reason =
    document.getElementById("reason").value;

    let leaveType =
    document.getElementById("leaveType").value;

    if(!from || !to || !days || !reason){

        alert("Please fill all fields");
        return;
    }

    const response = await fetch('/api/leave/apply',{

        method:'POST',

        headers:{
            'Content-Type':'application/json'
        },

        body:JSON.stringify({

            from_date:from,
            to_date:to,
            days:days,
            reason:reason,
            leave_type:leaveType

        })

    });

    const data = await response.json();

    alert(data.message || data.error);

    if(data.message){

        closeModal();

        loadDashboard();

        loadRequests();
    }

}

// LOAD REQUESTS
function loadRequests(tab = null){

    // ACTIVE TAB
    document.querySelectorAll(".leave-tab")
    .forEach(t => t.classList.remove("active"));

    if(tab){
        tab.classList.add("active");
    }else{
        document.querySelectorAll(".leave-tab")[0]
        .classList.add("active");
    }

    fetch('/api/leave/my_requests')

    .then(res => res.json())

    .then(data => {

        let body =
        document.getElementById("tbody");

        let head =
        document.getElementById("thead");

        // TABLE HEADERS
        head.innerHTML = `
        <tr>
            <th>From</th>
            <th>To</th>
            <th>Days</th>
            <th>Applied Time</th>
            <th>Leave Type</th>
            <th>Status</th>
            <th>Action</th>
        </tr>
        `;

        body.innerHTML = "";

        if(data.length === 0){

            body.innerHTML = `
            <tr>
                <td colspan="7">
                    No leave requests found
                </td>
            </tr>
            `;

            return;
        }

        data.forEach(r => {

            body.innerHTML += `

            <tr>

                <td>${r.start_date}</td>
                <td>${r.end_date}</td>
                <td>${r.total_days}</td>

                <td>${r.applied_time || '-'}</td>

                <td>${r.leave_type}</td>

                <td>
                    <span class="status ${r.status.toLowerCase()}">
                        ${r.status}
                    </span>
                </td>

                <td>

                    ${r.status == "Pending"
                    ?
                    `<button
                        class="leave-btn leave-close-btn"
                        onclick="cancelLeave(${r.leave_id})"
                    >
                        Cancel
                    </button>`
                    :
                    '-'
                    }

                </td>

            </tr>

            `;
        });

    });

}

// CANCEL LEAVE
function cancelLeave(id){

    fetch(`/api/leave/cancel/${id}`,{
        method:'POST'
    })

    .then(() => {

        loadRequests();

        loadDashboard();

    });

}

// FILTERS
function applyFilters(){

    let month =
    document.getElementById("monthFilter").value;

    let year =
    document.getElementById("yearFilter").value;

    let status =
    document.getElementById("statusFilter").value;

    let url =
    `/api/leave/my_requests?month=${month}&year=${year}&status=${status}`;

    fetch(url)

    .then(res => res.json())

    .then(data => {

        let body =
        document.getElementById("tbody");

        body.innerHTML = "";

        data.forEach(r => {

            body.innerHTML += `
            <tr>

                <td>${r.start_date}</td>
                <td>${r.end_date}</td>
                <td>${r.total_days}</td>


                <td>${r.applied_time || '-'}</td>

                <td>${r.leave_type}</td>

                <td>
                    <span class="status ${r.status.toLowerCase()}">
                        ${r.status}
                    </span>
                </td>

                <td>-</td>

            </tr>
            `;
        });

    });

}


// LOAD HISTORY
function loadHistory(tab){

    // active tab switch
    document.querySelectorAll(".leave-tab")
    .forEach(t => t.classList.remove("active"));

    tab.classList.add("active");

    fetch('/api/leave/history')

    .then(res => res.json())

    .then(data => {

        let body =
        document.getElementById("tbody");

        let head =
        document.getElementById("thead");

        // table headings
        head.innerHTML = `
        <tr>
            <th>From</th>
            <th>To</th>
            <th>Days</th>
            <th>Applied Time</th>
            <th>Leave Type</th>
            <th>Status</th>
            <th>Action</th>
        </tr>
        `;

        body.innerHTML = "";

        if(data.length === 0){

            body.innerHTML = `
            <tr>
                <td colspan="7">
                    No history found
                </td>
            </tr>
            `;

            return;
        }

        data.forEach(r => {

            body.innerHTML += `
            <tr>

                <td>${r.start_date}</td>
                <td>${r.end_date}</td>
                <td>${r.total_days}</td>


                <td>${r.applied_time || '-'}</td>

                <td>${r.leave_type}</td>

                <td>
                    <span class="status ${r.status.toLowerCase()}">
                        ${r.status}
                    </span>
                </td>

                <td>-</td>

            </tr>
            `;
        });

    });
  }



// AUTO YEAR
let yearSelect =
document.getElementById("yearFilter");

let currentYear =
new Date().getFullYear();

if(yearSelect){

    for(let y=currentYear; y<=currentYear+10; y++){

        let option =
        document.createElement("option");

        option.value = y;
        option.text = y;

        yearSelect.appendChild(option);
    }

}


// OPEN MODAL
// function openModal(){

//     document
//     .getElementById("modal")
//     .classList.add("show");

// }
  
// CLOSE MODAL
// function closeModal(){

//     document
//     .getElementById("modal")
//     .classList.remove("show");

// }



function searchTDS() {

    let quarter = document.getElementById("tds_quarter").value;
    let year = document.getElementById("tds_year").value;

    if (!quarter || !year) {
        alert("Select Quarter and Year");
        return;
    }

    fetch("/search_tds", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            quarter: quarter,
            year: year
        })
    })
    .then(res => res.json())
    .then(data => {

        let box = document.getElementById("tds_result");

        if (data.exists) {
            box.innerHTML = `
                <p><b>File:</b> ${data.file_name}</p>
                <a href="/download_tds/${data.tds_id}">
                    <button>Download</button>
                </a>
            `;
        } else {
            box.innerHTML = `<p style="color:red;">Not Uploaded</p>`;
        }

    });
}


function logout() {
    alert("Logout clicked");
    window.location.href = "/logout";
}

// document.addEventListener("DOMContentLoaded", function () {

//     if (showBirthdayPopup === "True") {
//         alert("🎂 Happy Birthday! Team PCE wishes you a wonderful year ahead.");
//     }

//     if (showAnniversaryPopup === "True") {
//         alert("🎉 Happy Work Anniversary! Thank you for being a valuable part of Team PCE.");
//     }

// });



document.addEventListener("DOMContentLoaded", function () {

    // BOTH
    if (showBirthdayPopup && showAnniversaryPopup) {

        document.getElementById("wishTitle").innerHTML =
            "🎂🎉 Double Celebration! <br> <br>";

        document.getElementById("wishMessage").innerHTML =
            "Happy Birthday and Happy Work Anniversary! Team PCE wishes you happiness, success, good health and many more wonderful years with us.";

        document.getElementById("wishModal").style.display = "block";
    }

    // BIRTHDAY ONLY
    else if (showBirthdayPopup) {

        document.getElementById("wishTitle").innerHTML =
            "🎂 Happy Birthday";

        document.getElementById("wishMessage").innerHTML =
            "Dear Employee,<br><br>" +
            "Wishing you happiness, success, prosperity and good health. " +
            "May this special day bring joy and wonderful memories. " +
            "Have an amazing birthday!";

        document.getElementById("wishModal").style.display = "block";
    }

    // ANNIVERSARY ONLY
    else if (showAnniversaryPopup) {

        document.getElementById("wishTitle").innerHTML =
            "🎉 Happy Work Anniversary";

        document.getElementById("wishMessage").innerHTML =
            "Dear Employee,<br><br>" +
            "Thank you for your dedication, commitment and contribution to PCE. " +
            "We appreciate your hard work and wish you continued success and growth.";

        document.getElementById("wishModal").style.display = "block";
    }

});

function closeWishPopup() {
    document.getElementById("wishModal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function () {

    const closeBtn = document.querySelector(".wish-close");

    if (closeBtn) {
        closeBtn.addEventListener("click", closeWishPopup);
    }

});

