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

function startGameBtnClick(){
    document.getElementById('startGameBtn').addEventListener("click", function (){
                window.location.href = "/waitingroom"
    });
}

function statsBtnClick(){
    document.getElementById('statsBtn').addEventListener("click", function (){
                window.location.href = "/stats"
    });
}

function startTusmoBtn(){
    document.getElementById('startTusmo').addEventListener("click", function (){
                window.location.href = "/tusmo"
    });
}



// Wait until DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    updateClock();
    startGameBtnClick();
    statsBtnClick();
    setInterval(updateClock, 1000);
});

const dictionary = "a"
const alphabet = ["A", "B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
function tusmoGame(){

}





document.addEventListener('DOMContentLoaded', function() {
    startTusmoBtn();
});