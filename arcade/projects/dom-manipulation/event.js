function changeColorEvent(event) {
    var triggerObject = event.target;
    document.getElementById("colorDiv").style.backgroundColor = triggerObject.innerHTML.toLowerCase();
}