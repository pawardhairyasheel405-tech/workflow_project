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




// APPROVE FINANCE
function approveFinance() {
    // update workflow stage
    localStorage.setItem("workflow_stage", "sent_to_ceo");

    alert("Finance Approval Completed — Sent to CEO");

    // WAIT THEN REDIRECT
    setTimeout(() => {
        window.location.href = "/ceo_dashboard";
    }, 900);
}
