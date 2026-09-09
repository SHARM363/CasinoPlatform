const API_URL = "https://casinoplatform.onrender.com";
const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

const balance = document.getElementById("balance");
const message = document.getElementById("message");
const depositForm = document.getElementById("depositForm");

async function loadUser() {
    try {
        const response = await fetch(`${API_URL}/api/me`, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();

        if (data.success) {
            balance.textContent = "৳" + Number(data.user.balance).toFixed(2);
        }
    } catch (err) {
        console.error(err);
    }
}

loadUser();

depositForm.onsubmit = async function (e) {
    e.preventDefault();

    const amount = document.getElementById("amount").value;
    const paymentMethod = document.getElementById("paymentMethod").value;

    message.textContent = "Submitting deposit...";

    try {
        const response = await fetch(`${API_URL}/api/deposit`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                amount,
                payment_method: paymentMethod
            })
        });

        const data = await response.json();

        if (data.success) {
            message.textContent = "Deposit request submitted successfully.";
            depositForm.reset();
        } else {
            message.textContent = data.message;
        }

    } catch (err) {
        message.textContent = "Server Error";
    }
};
