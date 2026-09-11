const API_URL = "https://casinoplatform.onrender.com";

alert("ADMIN JS LOADED");

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/api/admin/stats`);
        const data = await response.json();

        if (data.success) {
            document.getElementById("totalUsers").textContent =
                data.total_users;

            document.getElementById("totalBalance").textContent =
                "৳" + Number(data.total_balance).toFixed(2);

            document.getElementById("pendingDeposits").textContent =
                data.pending_deposits;

            document.getElementById("pendingWithdrawals").textContent =
                data.pending_withdrawals;
        }

    } catch (error) {
        console.error("Admin stats error:", error);
    }
}

loadStats();
async function loadUsers() {

    try {

        const response = await fetch(`${API_URL}/api/admin/users`);
        const data = await response.json();

        const usersList = document.getElementById("usersList");

        if (!data.success) {
            usersList.innerHTML = "Unable to load users.";
            return;
        }

        usersList.innerHTML = data.users.map(user => `
            <div class="card">
                <p><strong>ID:</strong> ${user.id}</p>
                <p><strong>Username:</strong> ${user.username}</p>
                <p><strong>Email:</strong> ${user.email}</p>
                <p><strong>Balance:</strong> ৳${Number(user.balance).toFixed(2)}</p>
            </div>
        `).join("");

    } catch (error) {
        console.error(error);
    }
}

loadUsers();
async function loadDeposits() {

    try {

        const response = await fetch(`${API_URL}/api/admin/deposits`);
        const data = await response.json();

        const depositsList = document.getElementById("depositsList");

        if (!data.success) {
            depositsList.innerHTML = "Unable to load deposits.";
            return;
        }

        if (data.deposits.length === 0) {
            depositsList.innerHTML = "No deposits found.";
            return;
        }

        depositsList.innerHTML = data.deposits.map(deposit => `
    <div class="card">

        <p><strong>ID:</strong> ${deposit.id}</p>

        <p><strong>User:</strong> ${deposit.username}</p>

        <p><strong>Amount:</strong> ৳${Number(deposit.amount).toFixed(2)}</p>

        <p><strong>Method:</strong> ${deposit.payment_method}</p>

        <p><strong>Status:</strong> ${deposit.status}</p>

        <button class="main-btn" onclick="approveDeposit(${deposit.id})">
            ✅ Approve
        </button>

        <button class="main-btn" onclick="rejectDeposit(${deposit.id})">
            ❌ Reject
        </button>

    </div>
`).join("");
    } catch (error) {
        console.error(error);
    }

}

loadDeposits();
async function approveDeposit(id) {

    try {

        const response = await fetch(
            `${API_URL}/api/admin/deposit/${id}/approve`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            loadDeposits();
            loadStats();
            loadUsers();
        } else {
            alert(data.message || "Approve failed.");
        }

    } catch (error) {

        console.error(error);
        alert(error);

    }

}

async function rejectDeposit(id) {

    try {

        const response = await fetch(
            `${API_URL}/api/admin/deposit/${id}/reject`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (data.success) {
            alert(data.message);
            loadDeposits();
            loadStats();
            loadUsers();
        } else {
            alert(data.message || "Reject failed.");
        }

    } catch (error) {

        console.error(error);
        alert(error);

    }

}
async function loadWithdrawals() {

    try {

        const response = await fetch(
            `${API_URL}/api/admin/withdrawals`
        );

        const data = await response.json();

        const withdrawalsList =
            document.getElementById("withdrawalsList");

        if (!data.success) {
            withdrawalsList.innerHTML =
                "Unable to load withdrawals.";
            return;
        }

        if (data.withdrawals.length === 0) {
            withdrawalsList.innerHTML =
                "No withdrawals found.";
            return;
        }

        withdrawalsList.innerHTML = data.withdrawals.map(withdrawal => `
            <div class="card">

                <p><strong>ID:</strong> ${withdrawal.id}</p>

                <p><strong>User ID:</strong> ${withdrawal.user_id}</p>

                <p><strong>Amount:</strong>
                    ৳${Number(withdrawal.amount).toFixed(2)}
                </p>

                <p><strong>Method:</strong>
const API_URL = "https://casinoplatform.onrender.com";


// ===============================
// ADMIN AUTHENTICATION
// ===============================

const adminToken = localStorage.getItem("admin_token");

if (!adminToken) {
    window.location.href = "admin-login.html";
}


// ===============================
// AUTHENTICATED FETCH
// ===============================

async function adminFetch(url, options = {}) {

    options.headers = {
        ...(options.headers || {}),
        "Authorization": "Bearer " + adminToken,
        "Content-Type": "application/json"
    };

    const response = await fetch(url, options);

    // Token expired / invalid
    if (response.status === 401) {

        localStorage.removeItem("admin_token");

        window.location.href = "admin-login.html";

        return null;
    }

    return response;
}


// ===============================
// ADMIN STATS
// ===============================

async function loadStats() {

    try {

        const response = await adminFetch(
            `${API_URL}/api/admin/stats`
        );

        if (!response) return;

        const data = await response.json();

        if (data.success) {

            document.getElementById("totalUsers").textContent =
                data.total_users;

            document.getElementById("totalBalance").textContent =
                "৳" + Number(data.total_balance).toFixed(2);

            document.getElementById("pendingDeposits").textContent =
                data.pending_deposits;

            document.getElementById("pendingWithdrawals").textContent =
                data.pending_withdrawals;
        }

    } catch (error) {

        console.error("Admin stats error:", error);

    }
}


// ===============================
// USERS
// ===============================

async function loadUsers() {

    try {

        const response = await adminFetch(
            `${API_URL}/api/admin/users`
        );

        if (!response) return;

        const data = await response.json();

        const usersList =
            document.getElementById("usersList");

        if (!data.success) {

            usersList.innerHTML =
                "Unable to load users.";

            return;
        }

        usersList.innerHTML = data.users.map(user => `

            <div class="card">

                <p>
                    <strong>ID:</strong>
                    ${user.id}
                </p>

                <p>
                    <strong>Username:</strong>
                    ${user.username}
                </p>

                <p>
                    <strong>Email:</strong>
                    ${user.email}
                </p>

                <p>
                    <strong>Balance:</strong>
                    ৳${Number(user.balance).toFixed(2)}
                </p>

            </div>

        `).join("");

    } catch (error) {

        console.error("Users error:", error);

    }
}


// ===============================
// DEPOSITS
// ===============================

async function loadDeposits() {

    try {

        const response = await adminFetch(
            `${API_URL}/api/admin/deposits`
        );

        if (!response) return;

        const data = await response.json();

        const depositsList =
            document.getElementById("depositsList");

        if (!data.success) {

            depositsList.innerHTML =
                "Unable to load deposits.";

            return;
        }

        if (data.deposits.length === 0) {

            depositsList.innerHTML =
                "No deposits found.";

            return;
        }

        depositsList.innerHTML = data.deposits.map(deposit => `

            <div class="card">

                <p>
                    <strong>ID:</strong>
                    ${deposit.id}
                </p>

                <p>
                    <strong>User:</strong>
                    ${deposit.username}
                </p>

                <p>
                    <strong>Amount:</strong>
                    ৳${Number(deposit.amount).toFixed(2)}
                </p>

                <p>
                    <strong>Method:</strong>
                    ${deposit.payment_method}
                </p>

                <p>
                    <strong>Status:</strong>
                    ${deposit.status}
                </p>

                ${
                    deposit.status === "pending"
                    ? `

                        <button
                            class="main-btn"
                            onclick="approveDeposit(${deposit.id})">
                            ✅ Approve
                        </button>

                        <button
                            class="main-btn"
                            onclick="rejectDeposit(${deposit.id})">
                            ❌ Reject
                        </button>

                    `
                    : ""
                }

            </div>

        `).join("");

    } catch (error) {

        console.error("Deposits error:", error);

    }
}


// ===============================
// APPROVE DEPOSIT
// ===============================

async function approveDeposit(id) {

    try {

        const response = await adminFetch(
            `${API_URL}/api/admin/deposit/${id}/approve`,
            {
                method: "POST"
            }
        );

        if (!response) return;

        const data = await response.json();

        if (data.success) {

            alert(data.message);

            loadDeposits();
            loadStats();
            loadUsers();

        } else {

            alert(
                data.message ||
                "Approve failed."
            );

        }

    } catch (error) {

        console.error(
            "Approve deposit error:",
            error
        );

        alert("Approve deposit failed.");

    }
}


// ===============================
// REJECT DEPOSIT
// ===============================

async function rejectDeposit(id) {

    try {

        const response = await adminFetch(
            `${API_URL}/api/admin/deposit/${id}/reject`,
            {
                method: "POST"
            }
        );

        if (!response) return;

        const data = await response.json();

        if (data.success) {

            alert(data.message);

            loadDeposits();
            loadStats();
            loadUsers();

        } else {

            alert(
                data.message ||
                "Reject failed."
            );

        }

    } catch (error) {

        console.error(
            "Reject deposit error:",
            error
        );

        alert("Reject deposit failed.");

    }
}


// ===============================
// WITHDRAWALS
// ===============================

async function loadWithdrawals() {

    try {

        const response = await adminFetch(
            `${API_URL}/api/admin/withdrawals`
        );

        if (!response) return;

        const data = await response.json();

        const withdrawalsList =
            document.getElementById(
                "withdrawalsList"
            );

        if (!data.success) {

            withdrawalsList.innerHTML =
                "Unable to load withdrawals.";

            return;
        }

        if (data.withdrawals.length === 0) {

            withdrawalsList.innerHTML =
                "No withdrawals found.";

            return;
        }

        withdrawalsList.innerHTML =
            data.withdrawals.map(withdrawal => `

            <div class="card">

                <p>
                    <strong>ID:</strong>
                    ${withdrawal.id}
                </p>

                <p>
                    <strong>User ID:</strong>
                    ${withdrawal.user_id}
                </p>

                <p>
                    <strong>Amount:</strong>
                    ৳${Number(withdrawal.amount).toFixed(2)}
                </p>

                <p>
                    <strong>Method:</strong>
                    ${withdrawal.payment_method}
                </p>

                <p>
                    <strong>Account:</strong>
                    ${withdrawal.account_number}
                </p>

                <p>
                    <strong>Status:</strong>
                    ${withdrawal.status}
                </p>

                ${
                    withdrawal.status === "pending"
                    ? `

                        <button
                            class="main-btn"
                            onclick="approveWithdrawal(${withdrawal.id})">
                            ✅ Approve
                        </button>

                        <button
                            class="main-btn"
                            onclick="rejectWithdrawal(${withdrawal.id})">
                            ❌ Reject
                        </button>

                    `
                    : ""
                }

            </div>

        `).join("");

    } catch (error) {

        console.error(
            "Withdrawals error:",
            error
        );

        document.getElementById(
            "withdrawalsList"
        ).innerHTML =
            "Unable to load withdrawals.";

    }
}


// ===============================
// APPROVE WITHDRAWAL
// ===============================

async function approveWithdrawal(id) {

    try {

        const response = await adminFetch(
            `${API_URL}/api/admin/withdraw/${id}/approve`,
            {
                method: "POST"
            }
        );

        if (!response) return;

        const data = await response.json();

        if (data.success) {

            alert(data.message);

            loadWithdrawals();
            loadStats();
            loadUsers();

        } else {

            alert(
                data.message ||
                "Approve failed."
            );

        }

    } catch (error) {

        console.error(
            "Approve withdrawal error:",
            error
        );

        alert(
            "Approve withdrawal failed."
        );

    }
}


// ===============================
// REJECT WITHDRAWAL
// ===============================

async function rejectWithdrawal(id) {

    try {

        const response = await adminFetch(
            `${API_URL}/api/admin/withdraw/${id}/reject`,
            {
                method: "POST"
            }
        );

        if (!response) return;

        const data = await response.json();

        if (data.success) {

            alert(data.message);

            loadWithdrawals();
            loadStats();
            loadUsers();

        } else {

            alert(
                data.message ||
                "Reject failed."
            );

        }

    } catch (error) {

        console.error(
            "Reject withdrawal error:",
            error
        );

        alert(
            "Reject withdrawal failed."
        );

    }
}


// ===============================
// LOAD EVERYTHING
// ===============================

loadStats();
loadUsers();
loadDeposits();
loadWithdrawals();
