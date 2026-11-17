// StockMaster Frontend Bootstrap Script
document.addEventListener("DOMContentLoaded", () => {
    const statusText = document.getElementById("status-text");
    if (statusText) {
        statusText.textContent = "StockMaster frontend initialized. Backend ready at http://127.0.0.1:8000.";
    }
});
