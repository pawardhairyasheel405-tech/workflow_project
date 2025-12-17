document.addEventListener("DOMContentLoaded", () => {
    loadAllComments();
});

// Load all comments from localStorage
function loadAllComments() {
    let historyBox = document.getElementById("commentHistory");
    historyBox.innerHTML = "";

    let engineer = JSON.parse(localStorage.getItem("engineer_comments")) || [];
    let deputy = JSON.parse(localStorage.getItem("deputy_comments")) || [];
    let finance = JSON.parse(localStorage.getItem("finance_comments")) || [];

    appendComments("Engineer", engineer, historyBox);
    appendComments("Deputy Engineer", deputy, historyBox);
    appendComments("Finance", finance, historyBox);
}

function appendComments(role, arr, container) {
    arr.forEach(text => {
        let div = document.createElement("div");
        div.className = "comment-item";
        div.innerHTML = `<b>${role}:</b> ${text}`;
        container.appendChild(div);
    });
}

// Approve final
function approveFinal() {
    alert("Final Approval Completed — Logging out...");
    
    // Clear comment input
    document.getElementById("commentInput").value = "";

    // Redirect to login page
    setTimeout(() => {
        window.location.href = "/login";
    }, 1200);
}

// Reject final
function rejectFinal() {
    alert("Document Rejected — Redirecting to Engineer Dashboard");

    setTimeout(() => {
        window.location.href = "/dashboard";
    }, 1200);
}
