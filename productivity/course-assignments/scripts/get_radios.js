// Extract all radio button labels from a LAMS quiz/assessment page
// Usage: osascript -e 'tell application "Safari" to do JavaScript (do shell script "cat /tmp/get_radios.js") in tab N of window M'
var r = document.querySelectorAll("input[type=radio]");
var s = "";
for (var i = 0; i < r.length; i++) {
    var l = r[i].nextElementSibling ? r[i].nextElementSibling.textContent.trim() : r[i].parentElement.textContent.trim();
    s += r[i].name + "=" + r[i].value + ": " + l.substring(0, 150) + "\n";
}
s;
