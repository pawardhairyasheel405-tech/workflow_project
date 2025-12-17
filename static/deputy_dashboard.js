document.addEventListener("DOMContentLoaded", loadComments);

// ADD COMMENT
document.addEventListener("DOMContentLoaded", loadComments);

const DOC_ID = 1;

async function addComment() {
    let text = document.getElementById("commentInput").value.trim();

    if (text === "") {
        alert("Comment cannot be empty!");
        return;
    }

    const res = await fetch(`/add_comment/${DOC_ID}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comment: text })
    });

    const data = await res.json();

    if (data.success) {
        document.getElementById("commentInput").value = "";
        loadComments();
    }
}

async function loadComments() {
    const res = await fetch(`/get_comments/${DOC_ID}`);
    const comments = await res.json();

    let list = document.getElementById("commentList");
    list.innerHTML = "";

    comments.forEach(c => {
        let div = document.createElement("div");
        div.className = "comment";
        div.innerHTML = `
            <b>${c.role}</b>: ${c.comment}<br>
            <small>${c.timestamp}</small>
        `;
        list.appendChild(div);
    });
}

a



// APPROVE — FIXED & WORKING
function approveDeputy() {
    console.log("Deputy approval function triggered"); // debug

    // (1) Update workflow
    localStorage.setItem("workflow_stage", "sent_to_finance");

    // (2) Notify user
    alert("Deputy Approval Completed — Sent to Finance Department");

    // (3) Redirect after short delay
    setTimeout(() => {
        window.location.href = "/finance_dashboard";
    }, 900);
}
