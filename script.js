const themeButton = document.getElementById("themeToggle");

const savedTheme = localStorage.getItem("taskflow-theme");

if (savedTheme === "light") {
    document.body.classList.add("light-mode");
}

if (themeButton) {
    themeButton.addEventListener("click", function () {
        document.body.classList.toggle("light-mode");

        const theme = document.body.classList.contains("light-mode")
            ? "light"
            : "dark";

        localStorage.setItem("taskflow-theme", theme);
    });
}

// Pomodoro Focus Timer
let timeLeft = 25 * 60;
let timerInterval = null;

const timerDisplay = document.getElementById("timer");
const startButton = document.getElementById("startTimer");
const pauseButton = document.getElementById("pauseTimer");
const resetButton = document.getElementById("resetTimer");

function updateTimer() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;

    timerDisplay.textContent =
        String(minutes).padStart(2, "0") + ":" +
        String(seconds).padStart(2, "0");
}

if (timerDisplay && startButton && pauseButton && resetButton) {
    updateTimer();

    startButton.addEventListener("click", function () {
        if (timerInterval !== null) return;

        timerInterval = setInterval(function () {
            if (timeLeft > 0) {
                timeLeft--;
                updateTimer();
            } else {
                clearInterval(timerInterval);
                timerInterval = null;
                alert("Focus session completed! Take a 5-minute break.");
            }
        }, 1000);
    });

    pauseButton.addEventListener("click", function () {
        clearInterval(timerInterval);
        timerInterval = null;
    });

    resetButton.addEventListener("click", function () {
        clearInterval(timerInterval);
        timerInterval = null;
        timeLeft = 25 * 60;
        updateTimer();
    });
}
