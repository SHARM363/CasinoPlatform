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
async function loadDepositHistory() {

    const history = document.getElementById("history");

    try {

        const response = await fetch(
            `${API_URL}/api/deposits`,
            {
                method: "GET",
                headers: {
                    "Authorization": "Bearer " + token
                }
            }
        );

        const data = await response.json();

        if (!data.success) {
            history.textContent = "Unable to load deposit history.";
            return;
        }

        if (!data.deposits || data.deposits.length === 0) {
            history.textContent = "No deposits yet.";
            return;
        }

        history.innerHTML = data.deposits.map(deposit => {

            let statusText = deposit.status;

            if (deposit.status === "pending") {
                statusText = "Processing";
            }

            return `
                <div class="card">
                    <p><strong>💳 Method:</strong> ${deposit.payment_method}</p>
                    <p><strong>💰 Amount:</strong> ৳${Number(deposit.amount).toFixed(2)}</p>
                    <p><strong>⏳ Status:</strong> ${statusText}</p>
                    <p><strong>🕐 Time:</strong> ${deposit.created_at}</p>
                </div>
            `;

        }).join("");

    } catch (error) {

        console.error("Deposit history error:", error);

        history.textContent =
            "Unable to load deposit history.";

    }
}

loadDepositHistory();
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
    loadUser();
    loadDepositHistory();
 } else {
    message.textContent = data.message || "Deposit request failed.";
 }

 } catch (err) {
    message.textContent = "Server Error";
 }
 };
