
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

console.log(compare("TACLE", "ACLET"));

