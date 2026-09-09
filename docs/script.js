const API_URL = "https://casinoplatform.onrender.com";

const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const message = document.getElementById("message");

// Login tab
loginTab.onclick = function () {
    loginTab.classList.add("active");
    registerTab.classList.remove("active");

    loginForm.style.display = "block";
    registerForm.style.display = "none";

    message.textContent = "";
};

// Register tab
registerTab.onclick = function () {
    registerTab.classList.add("active");
    loginTab.classList.remove("active");

    loginForm.style.display = "none";
    registerForm.style.display = "block";

    message.textContent = "";
};

// Register
registerForm.onsubmit = async function (e) {
    e.preventDefault();

    const username = document.getElementById("registerUsername").value.trim();
    const email = document.getElementById("registerEmail").value.trim();
    const password = document.getElementById("registerPassword").value;

    try {
        const response = await fetch(API_URL + "/api/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });

        const data = await response.json();

        if (data.success) {
            message.textContent = "Registration successful.";

            registerForm.reset();

            loginTab.click();

        } else {
            message.textContent = data.message;
        }

    } catch (err) {
        message.textContent = "Server Error";
    }
};

// Login
loginForm.onsubmit = async function (e) {

    e.preventDefault();

    const username_or_email =
        document.getElementById("loginUsername").value.trim();

    const password =
        document.getElementById("loginPassword").value;

    try {

        const response = await fetch(API_URL + "/api/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                username_or_email,
                password

            })

        });

        const data = await response.json();

        if (data.success) {

            localStorage.setItem("token", data.token);

            message.textContent = "Login successful.";

        } else {

            message.textContent = data.message;

        }

    } catch (err) {

        message.textContent = "Server Error";

    }

};
