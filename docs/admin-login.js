const API_URL = "https://casinoplatform.onrender.com";

document.getElementById("loginBtn").addEventListener("click", adminLogin);

async function adminLogin() {

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    const message = document.getElementById("message");

    if (!username || !password) {
        message.textContent = "Username and password are required.";
        return;
    }

    message.textContent = "Logging in...";

    try {

        const response = await fetch(
            `${API_URL}/api/admin/login`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (data.success) {

            localStorage.setItem(
                "admin_token",
                data.token
            );

            window.location.href = "admin.html";

        } else {

            message.textContent =
                data.message || "Admin login failed.";

        }

    } catch (error) {

        console.error("Admin login error:", error);

        message.textContent =
            "Unable to connect to server.";

    }
}
