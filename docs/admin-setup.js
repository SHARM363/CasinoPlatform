const API_URL = "https://casinoplatform.onrender.com";

const button = document.getElementById("createAdminBtn");
const message = document.getElementById("message");

button.addEventListener("click", async function () {

    const username =
        document.getElementById("username").value.trim();

    const password =
        document.getElementById("password").value;

    if (!username || !password) {

        message.textContent =
            "Username and password are required.";

        return;
    }

    if (password.length < 8) {

        message.textContent =
            "Password must be at least 8 characters.";

        return;
    }

    message.textContent = "Creating admin...";

    try {

        const response = await fetch(
            API_URL + "/api/admin/setup",
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

            message.textContent =
                "Admin account created successfully.";

            document.getElementById("username").value = "";
            document.getElementById("password").value = "";

        } else {

            message.textContent =
                data.message || "Admin creation failed.";

        }

    } catch (error) {

        console.error("Admin setup error:", error);

        message.textContent =
            "Server connection failed.";

    }

});
