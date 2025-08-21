
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

function compare (word, guessing){
    var splitted_to_guess = word.split("");
    var splitted_guessing = guessing.split("");
    var correct = [];
    var in_the_word = [];
    for (let index in splitted_guessing){
        var letter = splitted_guessing[index];
        if (splitted_to_guess.includes(letter)){
            var positions_of_letter_in_to_guess = [];
            for (let i = 0; i < splitted_to_guess.length; i++) {
                if (splitted_to_guess[i] === letter) {
                    positions_of_letter_in_to_guess.push(i);
                }
            }
            if (positions_of_letter_in_to_guess.includes(Number(index))) {
                correct.push(letter);
            }
            else{
                in_the_word.push(letter);
            }
        }
    }
    var return_Array = [correct, in_the_word];
    return return_Array;
}

function compare_founded_letters(all_correct_letters, all_in_word_letters, founded_letters, founded_in_word_letters) {
    for (let letter of founded_letters) {
        if (!(all_correct_letters.includes(letter))) {
            all_correct_letters.push(letter);
        }
    }
    for (let letter of founded_in_word_letters) {
        if (!(all_in_word_letters.includes(letter))) {
            all_in_word_letters.push(letter);
        }
    }
    return [all_correct_letters, all_in_word_letters];
}

// first, display the grid as many text zones. Each square is a text input
// then, need to assemble all the inputs as one words
// then compare() with the first words
// Then showing the result with all the correct letters at the right place

const choosen_word = "TEST";
const alphabet = ["A", "B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"];
var all_correct_letters = [];
var all_in_word_letters = [];



document.addEventListener('DOMContentLoaded', function() {
    startTusmoBtn();
});