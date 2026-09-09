const API_URL = "https://casinoplatform.onrender.com";

const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const message = document.getElementById("message");

loginTab.addEventListener("click", () => {
    loginTab.classList.add("active");
    registerTab.classList.remove("active");

    loginForm.style.display = "block";
    registerForm.style.display = "none";

    message.textContent = "";
});

registerTab.addEventListener("click", () => {
    registerTab.classList.add("active");
    loginTab.classList.remove("active");

    registerForm.style.display = "block";
    loginForm.style.display = "none";

    message.textContent = "";
});


// ====================
// REGISTER
// ====================

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username = document.getElementById("registerUsername").value.trim();
    const email = document.getElementById("registerEmail").value.trim();
    const password = document.getElementById("registerPassword").value;

    message.textContent = "Creating account...";

    try {
        const response = await fetch(`${API_URL}/api/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (data.success) {
            message.textContent = "Registration successful!";

            registerForm.reset();

            setTimeout(() => {
                loginTab.click();
            }, 1000);
        } else {
            message.textContent = data.message || "Registration failed.";
        }

    } catch (error) {
        console.error(error);
        message.textContent = "Server connection failed.";
    }
});


// ====================
// LOGIN
// ====================

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username_or_email =
        document.getElementById("loginUsername").value.trim();

    const password =
        document.getElementById("loginPassword").value;

    message.textContent = "Logging in...";

    try {
        const response = await fetch(`${API_URL}/api/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username_or_email: username_or_email,
                password: password
            })
        });

        const data = await response.json();

        if (data.success) {

            // Save JWT token
            localStorage.setItem("rsk32_token", data.token);

            message.textContent = "Login successful!";

            console.log("Login user:", data.user);
            console.log("JWT Token saved
