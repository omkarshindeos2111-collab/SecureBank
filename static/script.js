/* ==========================================
   SIDEBAR TOGGLE
========================================== */

// Prevent back button showing cached dashboard after logout
window.addEventListener("pageshow", function (event) {
    if (event.persisted || window.performance.getEntriesByType("navigation")[0].type === "back_forward") {
        window.location.reload();
    }
});

function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("active");
}

/* Close sidebar when clicking outside */
document.addEventListener("click", function (event) {

    let sidebar = document.getElementById("sidebar");
    let menuBtn = document.querySelector(".menu-btn");

    if (
        sidebar.classList.contains("active") &&
        !sidebar.contains(event.target) &&
        !menuBtn.contains(event.target)
    ) {
        sidebar.classList.remove("active");
    }

});

/* ==========================================
   SECTION SWITCHING
========================================== */

function hideAll() {
    document.getElementById("dashboardSection").classList.add("hidden");
    document.getElementById("historySection").classList.add("hidden");
    document.getElementById("securitySection").classList.add("hidden");
}

/* ==========================================
   SECTION SWITCHING + AUTO CLOSE SIDEBAR
========================================== */

function hideAll() {
    document.getElementById("dashboardSection").classList.add("hidden");
    document.getElementById("historySection").classList.add("hidden");
    document.getElementById("securitySection").classList.add("hidden");
}

function removeActiveMenu() {
    document.getElementById("menuDashboard").classList.remove("active");
    document.getElementById("menuHistory").classList.remove("active");
    document.getElementById("menuSecurity").classList.remove("active");
}

function closeSidebar() {
    document.getElementById("sidebar").classList.remove("active");
}

function showDashboard() {
    hideAll();
    removeActiveMenu();
    document.getElementById("dashboardSection").classList.remove("hidden");
    document.getElementById("menuDashboard").classList.add("active");
    closeSidebar();
}

function showHistory() {
    hideAll();
    removeActiveMenu();
    document.getElementById("historySection").classList.remove("hidden");
    document.getElementById("menuHistory").classList.add("active");
    closeSidebar();
}

function showSecurity() {
    hideAll();
    removeActiveMenu();
    document.getElementById("securitySection").classList.remove("hidden");
    document.getElementById("menuSecurity").classList.add("active");
    closeSidebar();
}

/* ==========================================
   CHANGE PASSWORD
========================================== */

function changePassword() {

    let currentPassword =
        document.getElementById("currentPassword").value.trim();

    let newPassword =
        document.getElementById("newPassword").value.trim();

    if (currentPassword === "" || newPassword === "") {
        alert("Please fill all fields");
        return;
    }

    fetch("/change_password", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword
        })
    })
    .then(response => response.json())
    .then(data => {

        alert(data.message);

        if (data.status === "success") {
            document.getElementById("currentPassword").value = "";
            document.getElementById("newPassword").value = "";
        }

    })
    .catch(error => {
        console.error("Error changing password:", error);
    });
}


/* ==========================================
   CHANGE PIN
========================================== */

function changePin() {

    let password =
        document.getElementById("loginPassword").value.trim();

    let newPin =
        document.getElementById("newPin").value.trim();

    if (password === "" || newPin === "") {
        alert("Please enter password and new PIN");
        return;
    }

    fetch("/change_pin", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            password: password,
            new_pin: newPin
        })
    })
    .then(response => response.json())
    .then(data => {

        alert(data.message);

        if (data.status === "success") {
            document.getElementById("loginPassword").value = "";
            document.getElementById("newPin").value = "";
        }

    })
    .catch(error => {
        console.error("Error changing PIN:", error);
    });
}

/* ==========================================
   TRANSACTION FILTER
========================================== */

function filterTransactions(type) {

    let rows = document.querySelectorAll(".transaction-row");

    rows.forEach(row => {

        if (type === "all") {
            row.style.display = "";
        } 
        else if (row.dataset.type === type) {
            row.style.display = "";
        } 
        else {
            row.style.display = "none";
        }

    });

}

/* ==========================================
   TRANSACTION FILTER
========================================== */

function filterTransactions(type) {

    let rows = document.querySelectorAll(".transaction-row");

    rows.forEach(row => {

        let rowType = row.getAttribute("data-type");

        if (type === "all") {
            row.style.display = "table-row";
        }
        else if (rowType === type) {
            row.style.display = "table-row";
        }
        else {
            row.style.display = "none";
        }

    });

}

/* ==========================================
   PROFILE DROPDOWN
========================================== */

function toggleProfileMenu() {
    document.getElementById("profileDropdown")
        .classList.toggle("hidden");
}

/* Close when clicking outside */
document.addEventListener("click", function (event) {

    let profileArea = document.getElementById("profileArea");
    let dropdown = document.getElementById("profileDropdown");

    if (
        !profileArea.contains(event.target)
    ) {
        dropdown.classList.add("hidden");
    }

});