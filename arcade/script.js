// EYE FOLLOW LOGIC
const pupilContainers = document.querySelectorAll('.pupil-container');

document.addEventListener('mousemove', (e) => {
    pupilContainers.forEach((container) => {
        const eye = container.parentElement;
        const eyeRect = eye.getBoundingClientRect();
        const eyeCenterX = eyeRect.left + (eyeRect.width / 2);
        const eyeCenterY = eyeRect.top + (eyeRect.height / 2);

        const angle = Math.atan2(e.clientY - eyeCenterY, e.clientX - eyeCenterX);
        const maxDistance = eyeRect.width / 6;
        const distance = Math.min(
            maxDistance,
            Math.hypot(e.clientX - eyeCenterX, e.clientY - eyeCenterY) / 5
        );

        const x = Math.cos(angle) * distance;
        const y = Math.sin(angle) * distance;

        container.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
    });
});


// EYE MOVES - for web & mobile
function updateEyePosition(clientX, clientY) {
    const pupilContainers = document.querySelectorAll('.pupil-container');

    pupilContainers.forEach((container) => {
        const eye = container.parentElement;
        const eyeRect = eye.getBoundingClientRect();
        const eyeCenterX = eyeRect.left + (eyeRect.width / 2);
        const eyeCenterY = eyeRect.top + (eyeRect.height / 2);

        // Calculate the angle
        const angle = Math.atan2(clientY - eyeCenterY, clientX - eyeCenterX);

        // Distance limit so pupils won't leak out of eyeballs :D 
        const maxDistance = eyeRect.width / 6;
        const distance = Math.min(
            maxDistance,
            Math.hypot(clientX - eyeCenterX, clientY - eyeCenterY) / 5
        );

        const x = Math.cos(angle) * distance;
        const y = Math.sin(angle) * distance;

        // Update the position
        container.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
    });
}

// Mouse listener - web
document.addEventListener('mousemove', (e) => {
    updateEyePosition(e.clientX, e.clientY);
});

// Touch listener - mobile
// "passive: true" for increased performance without blocking scroll
document.addEventListener('touchmove', (e) => {
    // Get the finger position info
    const touch = e.touches[0];
    updateEyePosition(touch.clientX, touch.clientY);
}, { passive: true });

// Click/touch snapshot
document.addEventListener('touchstart', (e) => {
    const touch = e.touches[0];
    updateEyePosition(touch.clientX, touch.clientY);
}, { passive: true });



// OVERLAY SECTION

const overlay = document.getElementById('game-overlay');
const frame = document.getElementById('project-frame');

// Open the project
function openProject(url) {
    frame.src = url;
    overlay.style.display = 'flex';
    // Animation
    setTimeout(() => {
        overlay.classList.add('active');
    }, 10);
}

// Close the project
function closeProject() {
    overlay.classList.remove('active');
    setTimeout(() => {
        overlay.style.display = 'none';
        frame.src = '';
    }, 300);
}

// Close if the background's clicked
overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
        closeProject();
    }
});


function openInNewTab() {
    const currentUrl = frame.src;
    if (currentUrl) {
        window.open(currentUrl, '_blank');
    }
}


// ESC key support addition for accessibility
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        if (overlay.style.display === "flex") {
            closeProject();
        }
    }
});