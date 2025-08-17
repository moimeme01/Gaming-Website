console.log("External JS loaded!");


function showMessage() {
    const output = document.getElementById('output');
    output.textContent = "Hello from external JS file!";
}

// Example: update clock every second
function updateClock() {
    const now = new Date();
    document.getElementById('clock').textContent = now.toLocaleTimeString();
}

// Wait until DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    updateClock();
    setInterval(updateClock, 1000);
});
