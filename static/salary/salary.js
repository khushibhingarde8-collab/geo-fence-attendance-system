// ================= OPEN SALARY SECTION =================

function openSalarySection(){

    showSection('salary');

    window.scrollTo({
        top:0,
        behavior:'smooth'
    });

}

// ================= CUSTOM TOP ALERT =================

function showTopAlert(message, type = "success") {

    const oldAlert = document.querySelector(".top-alert");

    if(oldAlert){
        oldAlert.remove();
    }

    const alertBox = document.createElement("div");

    alertBox.className = `top-alert ${type}`;

    alertBox.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">✖</button>
    `;

    document.body.appendChild(alertBox);

    setTimeout(() => {

        alertBox.classList.add("show");

    }, 100);

    setTimeout(() => {

        alertBox.classList.remove("show");

        setTimeout(() => {

            if(alertBox){
                alertBox.remove();
            }

        }, 500);

    }, 4000);
}

// ================= FILE NAME PREVIEW =================

document.addEventListener("DOMContentLoaded",()=>{

    const salaryFile =
    document.querySelector('input[name="salary_file"]');

    if(salaryFile){

        salaryFile.addEventListener("change",function(){

            if(this.files.length > 0){

                showTopAlert(
                    "Selected File: " + this.files[0].name,
                    "success"
                );
            }
        });
    }

});



    // ================= GENERATE SLIP =================

    const generateForm = document.querySelector(
        'form[action="/generate_salary_slip"]'
    );

    if(generateForm){

        generateForm.addEventListener("submit", () => {

            if(loadingOverlay){

                loadingOverlay.style.display = "flex";
            }

        });
    }

    // ================= UPLOAD SALARY SHEET =================

    const uploadForm = document.querySelector(
        'form[action="/upload_salary_sheet"]'
    );

    if(uploadForm){

        uploadForm.addEventListener("submit", function(e){

            e.preventDefault();

            if(loadingOverlay){

                loadingOverlay.style.display = "flex";
            }

            const formData = new FormData(uploadForm);

            fetch("/upload_salary_sheet", {

                method: "POST",
                body: formData

            })

            .then(response => response.json())

            .then(data => {

                if(loadingOverlay){

                    loadingOverlay.style.display = "none";
                }

                if(data.status === "success"){

                    showTopAlert(data.message, "success");

                    setTimeout(() => {

                        window.location.href = "/admin";

                    }, 1500);

                } else {

                    showTopAlert(data.message, "error");
                }

            })

            .catch(error => {

                if(loadingOverlay){

                    loadingOverlay.style.display = "none";
                }

                showTopAlert(
                    "Something went wrong",
                    "error"
                );

                console.log(error);

            });

        });
    }

    // ================= DELETE SALARY SHEET =================

    const deleteForm = document.querySelector(
        'form[action="/delete_salary_sheet"]'
    );

    if(deleteForm){

        deleteForm.addEventListener("submit", function(e){

            e.preventDefault();

            const confirmDelete = confirm(
                "Are you sure you want to delete this salary sheet?"
            );

            if(!confirmDelete){
                return;
            }

            if(loadingOverlay){

                loadingOverlay.style.display = "flex";
            }

            const formData = new FormData(deleteForm);

            fetch("/delete_salary_sheet", {

                method: "POST",
                body: formData

            })

            .then(response => response.json())

            .then(data => {

                if(loadingOverlay){

                    loadingOverlay.style.display = "none";
                }

                if(data.status === "success"){

                    showTopAlert(data.message, "success");

                    setTimeout(() => {

                        window.location.href = "/admin";

                    }, 1500);

                } else {

                    showTopAlert(data.message, "error");
                }

            })

            .catch(error => {

                if(loadingOverlay){

                    loadingOverlay.style.display = "none";
                }

                showTopAlert(
                    "Something went wrong",
                    "error"
                );

                console.log(error);

            });

        });
    }