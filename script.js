// Feature update: LOCALIZATION ENGINE - logic addition for language switcher

const DEFAULT_LANG = 'tr';
let currentLang = DEFAULT_LANG;

document.addEventListener("DOMContentLoaded", async function () {
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    const storedLang = localStorage.getItem('selectedLang');

    if (langParam && (langParam === 'tr' || langParam === 'en')) {
        currentLang = langParam;
    } else if (storedLang) {
        currentLang = storedLang;
    }

    await loadLanguage(currentLang);
    updateLangUI(currentLang);
});


// Switch languages
async function setLanguage(lang) {
    if (lang === currentLang) return;

    currentLang = lang;
    localStorage.setItem('selectedLang', lang);

    // Update URL without page reload
    const newUrl = new URL(window.location);
    newUrl.searchParams.set('lang', lang);
    window.history.pushState({}, '', newUrl);

    await loadLanguage(lang);
    updateLangUI(lang);
}


// Update JSON & map HTML
async function loadLanguage(lang) {
    try {
        const response = await fetch(`./locales/${lang}.json`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const translations = await response.json();

        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const value = key.split('.').reduce((obj, i) => (obj ? obj[i] : null), translations);

            if (value) {
                // innerHTML if there is an HTML tag, textContent if not
                if (value.includes('<')) {
                    element.innerHTML = value;
                } else {
                    element.textContent = value;
                }
            }
        });

        // Update HTML "lang" tag for SEO
        document.documentElement.lang = lang;

    } catch (error) {
        console.error("Dil dosyası yüklenemedi:", error);
    }
}

// UI Update
function updateLangUI(lang) {
    const btnTr = document.getElementById('btn-tr');
    const btnEn = document.getElementById('btn-en');

    if (!btnTr || !btnEn) return;

    if (lang === 'tr') {
        btnTr.className = 'lang-btn active';
        btnEn.className = 'lang-btn inactive';
    } else {
        btnEn.className = 'lang-btn active';
        btnTr.className = 'lang-btn inactive';
    }
}



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
        const message = "%cLooking under the hood? Nice! I bring QA precision to backend development. If you need a self-made .NET engineer who prioritizes scalable and robust architectures, say hi at nejlanurguney@gmail.com";
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