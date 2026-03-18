$(document).ready(function () {
    $(".JQButton").click(function () {
        $("#colorDiv").css("background-color", this.innerHTML.toLowerCase());
    });
});