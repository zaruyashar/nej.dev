// Navbar behaviour, console greeting and footer year.
document.addEventListener("DOMContentLoaded", function () {
    // navbar scroll efx
    const navbar = document.querySelector(".navbar");

    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            navbar.classList.add("shadow-sm");
        } else {
            navbar.classList.remove("shadow-sm");
        }
    });



    document.addEventListener("click", function (event) {
        var navbarCollapse = document.getElementById("navbarNav");
        var toggler = document.querySelector(".navbar-toggler");


        if (navbarCollapse.classList.contains("show") && !navbarCollapse.contains(event.target) && !toggler.contains(event.target)) {

            var bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                toggle: false
            });
            bsCollapse.hide();
        }
    });



    // greet recruiter
    if (typeof console !== 'undefined' && typeof console.log === 'function') {
        const message = "%cLooking under the hood? Nice! I bring QA precision to backend and AI engineering, and I design for security from the start. If you need a self-made .NET engineer who prioritizes scalable, robust, secure-by-design architectures, say hi at nejla@nej.dev";
        const style = "color: #2563eb; font-size: 16px; font-weight: bold;";

        try {
            console.log(message, style);
        } catch (error) {

        }
    }
});


const yearElement = document.getElementById('current-year');
if (yearElement) {
    const currentYear = new Date().getFullYear();
    yearElement.textContent = currentYear;
}