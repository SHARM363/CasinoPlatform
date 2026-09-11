const API_URL = "https://casinoplatform.onrender.com";
const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "index.html";
}

const balance = document.getElementById("balance");
const message = document.getElementById("message");
const depositForm = document.getElementById("depositForm");

const paymentMethod = document.getElementById("paymentMethod");
const paymentInfo = document.getElementById("paymentInfo");
const paymentTitle = document.getElementById("paymentTitle");
const paymentInstruction = document.getElementById("paymentInstruction");
const paymentValue = document.getElementById("paymentValue");
const copyPaymentBtn = document.getElementById("copyPaymentBtn");
const transactionId = document.getElementById("transactionId");

let paymentSettings = [];


/* ===============================
   LOAD USER
================================ */

async function loadUser() {

    try {

        const response = await fetch(
            `${API_URL}/api/me`,
            {
                headers: {
                    "Authorization": "Bearer " + token
                }
            }
        );

        const data = await response.json();

        if (data.success) {

            balance.textContent =
                "৳" + Number(data.user.balance).toFixed(2);

        }

    } catch (err) {

        console.error("Load user error:", err);

    }
}


/* ===============================
   LOAD PAYMENT SETTINGS
================================ */

async function loadPaymentSettings() {

    try {

        const response = await fetch(
            `${API_URL}/api/payment-settings`
        );

        const data = await response.json();

        if (!data.success) {

            console.error(
                "Payment settings error:",
                data.message
            );

            return;
        }

        paymentSettings = data.settings || [];

    } catch (error) {

        console.error(
            "Payment settings error:",
            error
        );

    }
}


/* ===============================
   SHOW PAYMENT INFORMATION
================================ */

paymentMethod.addEventListener(
    "change",
    function () {

        const method = this.value;

        if (!method) {

            paymentInfo.style.display = "none";
            return;

        }

        const setting = paymentSettings.find(
            item => item.payment_method === method
        );

        if (!setting) {

            paymentInfo.style.display = "block";

            paymentTitle.textContent =
                method.toUpperCase();

            paymentInstruction.textContent =
                "Payment method is currently unavailable.";

            paymentValue.textContent = "";

            return;
        }


        /* bKash / Nagad / Rocket */

        if (
            method === "bkash" ||
            method === "nagad" ||
            method === "rocket"
        ) {

            paymentInfo.style.display = "block";

            paymentTitle.textContent =
                method.charAt(0).toUpperCase() +
                method.slice(1);

            let typeText = "Send Money";

            if (setting.payment_type === "cash_out") {
                typeText = "Cash Out";
            }

            paymentInstruction.textContent =
                "Please " +
                typeText +
                " to the number below:";

            paymentValue.textContent =
                setting.payment_number || "";

        }


        /* USDT */

        if (method === "usdt") {

            paymentInfo.style.display = "block";

            paymentTitle.textContent =
                "USDT";

            paymentInstruction.textContent =
                "Send USDT using " +
                (setting.usdt_network || "TRC20") +
                " network to:";

            paymentValue.textContent =
                setting.usdt_address || "";

        }

    }
);


/* ===============================
   COPY PAYMENT NUMBER / ADDRESS
================================ */

copyPaymentBtn.addEventListener(
    "click",
    async function () {

        const value =
            paymentValue.textContent.trim();

        if (!value) {

            return;

        }

        try {

            await navigator.clipboard.writeText(value);

            copyPaymentBtn.textContent =
                "✅ Copied";

            setTimeout(() => {

                copyPaymentBtn.textContent =
                    "📋 Copy";

            }, 2000);

        } catch (error) {

            console.error(
                "Copy error:",
                error
            );

            alert("Unable to copy. Please copy manually.");

        }

    }
);


/* ===============================
   LOAD DEPOSIT HISTORY
================================ */

async function loadDepositHistory() {

    const history =
        document.getElementById("history");

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

            history.textContent =
                "Unable to load deposit history.";

            return;
        }

        if (
            !data.deposits ||
            data.deposits.length === 0
        ) {

            history.textContent =
                "No deposits yet.";

            return;
        }

        history.innerHTML =
            data.deposits.map(deposit => {

                let statusText =
                    deposit.status;

                if (deposit.status === "pending") {
                    statusText = "Processing";
                }

                return `
                    <div class="card">

                        <p>
                            <strong>💳 Method:</strong>
                            ${deposit.payment_method}
                        </p>

                        <p>
                            <strong>💰 Amount:</strong>
                            ৳${Number(deposit.amount).toFixed(2)}
                        </p>

                        <p>
                            <strong>🧾 Transaction ID:</strong>
                            ${deposit.transaction_id || "N/A"}
                        </p>

                        <p>
                            <strong>⏳ Status:</strong>
                            ${statusText}
                        </p>

                        <p>
                            <strong>🕐 Time:</strong>
                            ${deposit.created_at}
                        </p>

                    </div>
                `;

            }).join("");

    } catch (error) {

        console.error(
            "Deposit history error:",
            error
        );

        history.textContent =
            "Unable to load deposit history.";

    }
}


/* ===============================
   SUBMIT DEPOSIT
================================ */

depositForm.onsubmit = async function (e) {

    e.preventDefault();

    const amount =
        document.getElementById("amount").value;

    const method =
        paymentMethod.value;

    const txId =
        transactionId.value.trim();


    if (!method) {

        message.textContent =
            "Please select a payment method.";

        return;

    }


    if (!amount) {

        message.textContent =
            "Please enter deposit amount.";

        return;

    }


    if (!txId) {

        message.textContent =
            "Please enter Transaction ID.";

        transactionId.focus();

        return;

    }


    message.textContent =
        "Submitting deposit...";


    try {

        const response = await fetch(
            `${API_URL}/api/deposit`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },

                body: JSON.stringify({

                    amount: amount,

                    payment_method: method,

                    transaction_id: txId

                })

            }
        );


        const data =
            await response.json();


        if (data.success) {

            message.textContent =
                "✅ Deposit request submitted successfully. Please wait for admin approval.";

            depositForm.reset();

            paymentInfo.style.display =
                "none";

            await loadUser();

            await loadDepositHistory();

        } else {

            message.textContent =
                data.message ||
                "Deposit request failed.";

        }

    } catch (err) {

        console.error(
            "Deposit error:",
            err
        );

        message.textContent =
            "Server Error. Please try again.";

    }

};


/* ===============================
   INITIAL LOAD
================================ */

loadUser();
loadPaymentSettings();
loadDepositHistory();
