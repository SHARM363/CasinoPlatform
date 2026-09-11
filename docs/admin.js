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

console.log("STATS STATUS:", response.status);

const data = await response.json();

console.log("STATS DATA:", data);

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

        if (!data.users || data.users.length === 0) {

            usersList.innerHTML =
                "No users found.";

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

        if (!data.deposits || data.deposits.length === 0) {

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
                    ${deposit.username || deposit.user_id}
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

        document.getElementById(
            "depositsList"
        ).innerHTML =
            "Unable to load deposits.";

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

            alert(data.message || "Deposit approved.");

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

            alert(data.message || "Deposit rejected.");

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

        if (
            !data.withdrawals ||
            data.withdrawals.length === 0
        ) {

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
                            ✅
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

        console.error("Withdrawals error:", error);

        document.getElementById(
            "withdrawalsList"
        ).innerHTML =
            "Unable to load withdrawals.";

    }
}


// ===============================
// LOAD ALL ADMIN DATA
// ===============================

loadStats();
loadUsers();
loadDeposits();
loadWithdrawals();
