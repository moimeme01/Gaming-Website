
var all_correct_letters = [];
var all_in_word_letters = [];


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
    return [correct, in_the_word];
}

//console.log(compare("TACLE", "ACLET"));

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


//console.log(compare_founded_letters(["T"],["R"],["T"], ["R","E"]));


function random_word(dictionnaire) {
    let endIndex = dictionnaire.length;
    let choosen_one = Math.floor(Math.random() * endIndex);
    return (dictionnaire[choosen_one]);
}



