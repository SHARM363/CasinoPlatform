const API_URL = "https://casinoplatform.onrender.com";
const token = localStorage.getItem("token");

if (!token) {
window.location.href = "index.html";
}

const balance = document.getElementById("balance");
const message = document.getElementById("message");
const withdrawForm = document.getElementById("withdrawForm");

async function loadUser() {

try {

    const response = await fetch(`${API_URL}/api/me`, {
        method: "GET",
        headers: {
            "Authorization": "Bearer " + token
        }
    });

    const data = await response.json();

    if (data.success) {

        balance.textContent =
            "৳" + Number(data.user.balance || 0).toFixed(2);

    } else {

        localStorage.removeItem("token");
        window.location.href = "index.html";

    }

} catch (error) {

    console.error("Account error:", error);

}

}

loadUser();

withdrawForm.onsubmit = async function (e) {

e.preventDefault();

const amount =
    Number(document.getElementById("amount").value);

const paymentMethod =
    document.getElementById("paymentMethod").value;

const accountNumber =
    document.getElementById("accountNumber").value.trim();

if (amount < 300 || amount > 25000) {

    message.textContent =
        "Withdraw amount must be between ৳300 and ৳25,000.";

    return;
}

if (!accountNumber) {

    message.textContent =
        "Please enter your bKash or Nagad number.";

    return;
}

message.textContent = "Submitting withdraw request...";

try {

    const response = await fetch(
        `${API_URL}/api/withdraw`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                amount: amount,
                payment_method: paymentMethod,
                account_number: accountNumber
            })
        }
    );

    const data = await response.json();

    if (data.success) {

        message.textContent =
            "Withdraw request submitted successfully.";

        withdrawForm.reset();

        loadUser();

    } else {

        message.textContent =
            data.message || "Withdraw request failed.";

    }

} catch (error) {

    console.error("Withdraw error:", error);

    message.textContent =
        "Server Error. Please try again.";

}

};
