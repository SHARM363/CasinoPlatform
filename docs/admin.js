const API_URL = "https://casinoplatform.onrender.com";

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
            </div>
        `).join("");

    } catch (error) {
        console.error(error);
    }

}

loadDeposits();
