// Click the "Next Activity" button in LAMS
// Usage: osascript -e 'tell application "Safari" to do JavaScript (do shell script "cat /tmp/click_next.js") in tab N of window M'
var links = document.querySelectorAll("a, button");
for (var i = 0; i < links.length; i++) {
    if (links[i].textContent.trim().indexOf("Next Activity") !== -1) {
        links[i].click();
        "clicked: " + links[i].tagName;
        break;
    }
}
