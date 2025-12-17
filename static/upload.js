let dropArea = document.getElementById("dropArea");
let fileInput = document.getElementById("fileInput");
let fileInfo = document.getElementById("fileInfo");

// Click to open file dialog
dropArea.addEventListener("click", () => {
    fileInput.click();
});

// Handle file selection
fileInput.addEventListener("change", function () {
    handleFile(this.files[0]);
});

// Drag Over effect
dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.style.background = "#e2f0ff";
});

// Drag Leave
dropArea.addEventListener("dragleave", () => {
    dropArea.style.background = "#ffffffcc";
});

// Drop file
dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.style.background = "#ffffffcc";

    let file = e.dataTransfer.files[0];
    fileInput.files = e.dataTransfer.files; // Attach file to input
    handleFile(file);
});

// Validate and preview
function handleFile(file) {
    if (!file) return;

    if (file.type !== "sample.pdf") {
        alert("Only PDF files are allowed!");
        fileInput.value = "";
        fileInfo.innerHTML = "";
        return;
    }

    fileInfo.innerHTML = `Selected File: <b>${file.name}</b>`;
}
