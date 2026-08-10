document.addEventListener("DOMContentLoaded", () => {
    const checkboxes = document.querySelectorAll(".rubric-checkbox");
    const ringFill = document.getElementById("ring-fill");
    const percentageBadge = document.getElementById("percentage-badge");
    const scoreText = document.getElementById("score-text");
    const statusText = document.getElementById("status-text");
    const progressContainer = document.getElementById("progress-container");
    const modal = document.getElementById('details-modal');
    const startBtn = document.getElementById('submit-details-btn');
    const inputUrl = document.getElementById('input-prob-url');
    const inputname = document.getElementById("input-prob-name");
    const displayName = document.getElementById('display-prob-name');
    const displayUrl = document.getElementById('display-prob-url');
    const inputDiff = document.getElementById('input-prob-diff');
    const displayDiff = document.getElementById('display-prob-difficulty');

    const audio = new Audio('https://www.myinstants.com/media/sounds/gta-san-andreas-gorevi-gecme-muzigi-respect-mp3indirdur.mp3');

    let formPayload = { url: "", name: "", difficulty: "" };

    function updatePayload(percent) {
        formPayload = {
            url: inputUrl.value.trim(),
            name: inputname.value.trim(),
            difficulty: inputDiff.value.toLowerCase().trim(),
            percent: percent
        };
    }

    const totalMarks = 100;
    const targetFloor = 95;

    const CIRCUMFERENCE = 2 * Math.PI * 100;
    ringFill.style.strokeDasharray = `${CIRCUMFERENCE}`;

    let isTargetReachedPreviously = false;

    startBtn.addEventListener('click', () => {
        // Fix for problem name loading bug (.value instead of .innerText)
        const urlValue = inputUrl.value.trim();
        const nameValue = inputname.value.trim();
        const diffValue = inputDiff.value.toLowerCase().trim(); // 'easy', 'medium', or 'hard'

        // Update link text and href
        displayUrl.href = urlValue;
        displayUrl.textContent = nameValue;
        displayUrl.style.display = 'inline-block'; 
        
        // Dynamic Difficulty Tag Logic
        displayDiff.textContent = diffValue.charAt(0).toUpperCase() + diffValue.slice(1); // Capitalizes first letter
        
        // Remove any old difficulty classes to prevent color styling conflicts
        displayDiff.classList.remove('tag-easy', 'tag-medium', 'tag-hard');
        
        // Add the correct matching modifier class (tag-easy, tag-medium, or tag-hard)
        displayDiff.classList.add(`tag-${diffValue}`);
        displayDiff.style.display = 'inline-block'; // Shows tag once modal is saved
        
        modal.classList.add('hidden');
    });


    updateProgress()

    // Main recalculation logic
    function updateProgress() {
        let percentage = 0;

        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                percentage += parseInt(checkbox.dataset.marks, 10);
            }
        });


        const formattedPercentage = Math.round(percentage)

        const required = document.getElementById("required-accuracy-display");
        required.textContent = Math.round(100 - percentage) + "%";

        // Update Circular Stroke Offset
        const strokeOffset = CIRCUMFERENCE - (percentage / 100) * CIRCUMFERENCE;
        ringFill.style.strokeDashoffset = strokeOffset;

        // Update textual readouts
        percentageBadge.textContent = `${formattedPercentage}%`;
        scoreText.textContent = `${percentage} / ${totalMarks}`;

        updatePayload(percentage)

        // Target Achievement Check
        if (percentage >= targetFloor) {
            statusText.textContent = `Optimal Target Reached (≥ ${targetFloor}%)`;
            progressContainer.classList.add("target-reached");

            // Trigger animation effect on first target hit
            if (!isTargetReachedPreviously) {
                triggerCelebration();
                triggerGtaCelebration();
                isTargetReachedPreviously = true;
            }
        } else {
            statusText.textContent = `Floor Target Unreached (< ${targetFloor}%)`;
            progressContainer.classList.remove("target-reached");
            isTargetReachedPreviously = false;
        }
    }

    // Canvas Confetti Particles Animation
    function triggerCelebration() {
        const canvas = document.getElementById("confetti-canvas");
        const ctx = canvas.getContext("2d");

        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const particles = [];
        const colors = ["#22c55e", "#38bdf8", "#f59e0b", "#ec4899", "#8b5cf6"];

        for (let i = 0; i < 100; i++) {
            particles.push({
                x: window.innerWidth / 2,
                y: window.innerHeight / 3,
                vx: (Math.random() - 0.5) * 12,
                vy: (Math.random() - 0.7) * 12,
                size: Math.random() * 8 + 4,
                color: colors[Math.floor(Math.random() * colors.length)],
                alpha: 1,
                decay: Math.random() * 0.015 + 0.008
            });
        }

        function animateConfetti() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            let activeParticles = 0;
            particles.forEach(p => {
                if (p.alpha > 0) {
                    p.x += p.vx;
                    p.y += p.vy;
                    p.vy += 0.25; // gravity
                    p.alpha -= p.decay;

                    ctx.save();
                    ctx.globalAlpha = Math.max(0, p.alpha);
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();

                    activeParticles++;
                }
            });

            if (activeParticles > 0) {
                requestAnimationFrame(animateConfetti);
            } else {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }

        animateConfetti();
    }

    function triggerGtaCelebration() {
        const overlay = document.getElementById('gta-overlay');
        
        // Play GTA Mission Passed Sound Effect (Optional - add a sound file to assets)
        audio.play().catch(e => console.log(e));

        // Activate Overlay Elements
        overlay.classList.add('active');

        // Auto-dismiss the pop-up banner after 4.5 seconds
        setTimeout(() => {
            overlay.classList.remove('active');
        }, 4500);
    }

    window.addEventListener('pagehide', (event) => {
    const jsonString = JSON.stringify(formPayload);

    // Modern browsers guarantee this fires on page exit if keepalive is true
    fetch("/updatekeep", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: jsonString,
            keepalive: true // 👈 This is the crucial flag!
        });
    });


    // Attach listener to checkboxes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", (e) => {
            updateProgress();
        });
    });
});