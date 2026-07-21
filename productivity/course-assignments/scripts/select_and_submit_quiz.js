// Select quiz answers and submit
// Usage: Edit the answers object, then run via osascript
// osascript -e 'tell application "Safari" to do JavaScript (do shell script "cat /tmp/select_and_submit.js") in tab N of window M'

// === EDIT THIS: question_name -> correct_value ===
var answers = {
    "q1": "B",
    "q2": "A",
    "q3": "C",
    "q4": "B",
    "q5": "D",
    "q6": "A",
    "q7": "B",
    "q8": "C",
    "q9": "A",
    "q10": "B"
};

// Select answers
var radios = document.querySelectorAll("input[type=radio]");
var selected = 0;
for (var i = 0; i < radios.length; i++) {
    if (answers[radios[i].name] === radios[i].value) {
        radios[i].click();
        selected++;
    }
}

// Submit
var btn = document.querySelector(".submit-btn");
if (btn) {
    btn.click();
    "selected=" + selected + " submitted";
} else {
    "selected=" + selected + " no_submit_btn";
}
