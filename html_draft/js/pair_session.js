
var editor = CodeMirror.fromTextArea(document.getElementById("coding_area"), {
    lineNumbers: true,
    mode: "javascript",
    indentUnit: 4,
    indentWithTabs: true,
    enterMode: "keep",
    tabMode: "shift",
    theme: 'solarized dark'
});