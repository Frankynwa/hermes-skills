// Extract MathJax alt text from labels (for math-rendered options)
// Usage: osascript -e 'tell application "Safari" to do JavaScript (do shell script "cat /tmp/get_mathjax.js") in tab N of window M'
var questions = [3, 5, 6, 7]; // Adjust question indices as needed
var result = "";
for (var q = 0; q < questions.length; q++) {
    var name = "question" + questions[q];
    var labels = document.querySelectorAll("label[for^=" + name + "]");
    result += "Q" + (questions[q] + 1) + ":\n";
    for (var i = 0; i < labels.length; i++) {
        var img = labels[i].querySelector("img[data-jlatexmath]");
        var alt = img ? img.alt : labels[i].textContent.trim();
        result += "  " + alt + "\n";
    }
}
result || "no math found";
