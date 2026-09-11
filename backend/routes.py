from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection
from config import Config
import jwt
import datetime
def verify_admin_token():

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    if not auth_header.startswith("Bearer "):
        return None

    try:

        token = auth_header.split(" ", 1)[1]

        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=["HS256"]
        )

        if payload.get("role") != "admin":
            return None

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None

    except Exception:
        return None


api = Blueprint("api", __name__)


@api.route("/api")
def api_home():
    return jsonify({
        "success": True,
        "message": "CasinoPlatform API is working"
    })


@api.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid JSON data."
        }), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    referral_id = data.get("referral_id")
    # Check required fields
    if not username or not email or not password:
        return jsonify({
            "success": False,
            "message": "All fields are required."
        }), 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Check if username or email already exists
        cur.execute(
            """
            SELECT id
            FROM users
            WHERE username = %s OR email = %s
            """,
            (username, email)
        )

        existing_user = cur.fetchone()

        if existing_user:
            return jsonify({
                "success": False,
                "message": "Username or Email already exists."
            }), 409

        # Hash password before saving to database
        password_hash = generate_password_hash(password)

        # Create new user
        cur.execute(
            """
            INSERT INTO users (
                username,
                email,
                password
            )
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (
                username,
                email,
                password_hash
            )
        )

        user = cur.fetchone()
        user = cur.fetchone()

        # Create referral record
        if referral_id:

            try:
                referral_id = int(referral_id)

                # Make sure referrer exists
                cur.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE id = %s
                    """,
                    (referral_id,)
                )

                referrer = cur.fetchone()

                # Don't allow self-referral
                if referrer and referral_id != user["id"]:

                    cur.execute(
                        """
                        INSERT INTO referrals (
                            referrer_id,
                            referred_id,
                            reward
                        )
                        VALUES (%s, %s, %s)
                        """,
                        (
                            referral_id,
                            user["id"],
                            0
                        )
                    )

            except (ValueError, TypeError):
                pass

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Registration successful.",
            "user_id": user["id"]
        }), 201

    except Exception as e:

        if conn:
            conn.rollback()

        return jsonify({
            "success": False,
            "message": "Registration failed.",
            "error": str(e)
        }), 500

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()
# =========================
# USER LOGIN
# =========================
@api.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Invalid JSON data."
        }), 400

    username_or_email = data.get("username_or_email")
    password = data.get("password")

    # Check required fields
    if not username_or_email or not password:
        return jsonify({
            "success": False,
            "message": "Username/Email and password are required."
        }), 400

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        # Find user by username or email
        cur.execute(
            """
            SELECT id, username, email, password
            FROM users
            WHERE username = %s OR email = %s
            LIMIT 1
            """,
            (username_or_email, username_or_email)
        )

        user = cur.fetchone()

        # User not found
        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid username/email or password."
            }), 401

        # Check hashed password
        if not check_password_hash(user["password"], password):
            return jsonify({
                "success": False,
                "message": "Invalid username/email or password."
            }), 401

        # Generate JWT Token
        token = jwt.encode(
            {
                "user_id": user["id"],
                "username": user["username"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
            },
            Config.SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
        }), 200
    except Exception as e:

        if conn:
            conn.rollback()

        return jsonify({
            "success": False,
            "message": "Login failed.",
            "error": str(e)
        }), 500

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()
# Get logged-in user's profile and balance
@api.route("/api/me", methods=["GET"])
def get_me():

    try:

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "success": False,
                "message": "Authorization token required."
            }), 401

        token = auth_header.split(" ")[1]

        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload.get("user_id")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                username,
                email,
                balance
            FROM users
            WHERE id = %s
        """, (user_id,))

        user = cur.fetchone()

        cur.close()
        conn.close()

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        return jsonify({
            "success": True,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "balance": user["balance"]
            }
        }), 200

    except jwt.ExpiredSignatureError:

        return jsonify({
            "success": False,
            "message": "Token expired."
        }), 401

    except jwt.InvalidTokenError:

        return jsonify({
            "success": False,
            "message": "Invalid token."
        }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
@api.route("/api/test-balance", methods=["GET"])
def test_balance():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET balance = 1000
        WHERE id = 1
    """)

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Balance updated to 1000"
    })
@api.route("/api/deposit", methods=["POST"])
def create_deposit():

    token = request.headers.get("Authorization")

    if not token:
        return jsonify({
            "success": False,
            "message": "Authorization token required."
        }), 401

    try:

        token = token.replace("Bearer ", "")

        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload["user_id"]

        data = request.get_json() or {}

        amount = float(data.get("amount", 0))
        payment_method = data.get("payment_method")
        transaction_id = data.get("transaction_id", "").strip()

        # Amount validation
        if amount < 100:
            return jsonify({
                "success": False,
                "message": "Minimum deposit amount is ৳100."
            }), 400

        if amount > 25000:
            return jsonify({
                "success": False,
                "message": "Maximum deposit amount is ৳25,000."
            }), 400

        # Payment method validation
        if payment_method not in ["bkash", "nagad", "rocket", "usdt"]:
            return jsonify({
                "success": False,
                "message": "Invalid payment method."
            }), 400

        # Transaction ID validation
        if not transaction_id:
            return jsonify({
                "success": False,
                "message": "Transaction ID is required."
            }), 400

        if len(transaction_id) > 100:
            return jsonify({
                "success": False,
                "message": "Transaction ID is too long."
            }), 400

        conn = get_connection()
        cur = conn.cursor()

        # Create pending deposit request
        cur.execute("""
            INSERT INTO deposits
            (
                user_id,
                amount,
                payment_method,
                transaction_id,
                status
            )
            VALUES (%s, %s, %s, %s, 'pending')
            RETURNING id
        """, (
            user_id,
            amount,
            payment_method,
            transaction_id
        ))

        deposit = cur.fetchone()

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Deposit request submitted successfully.",
            "deposit_id": deposit["id"],
            "amount": amount,
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "status": "pending"
        }), 200

    except jwt.ExpiredSignatureError:

        return jsonify({
            "success": False,
            "message": "Token expired."
        }), 401

    except jwt.InvalidTokenError:

        return jsonify({
            "success": False,
            "message": "Invalid token."
        }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
@api.route("/api/withdraw", methods=["POST"])
def create_withdraw():

    token = request.headers.get("Authorization")

    if not token:
        return jsonify({
            "success": False,
            "message": "Authorization token required."
        }), 401

    try:
        token = token.replace("Bearer ", "")

        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload["user_id"]

        data = request.get_json() or {}

        amount = float(data.get("amount", 0))
        payment_method = data.get("payment_method")
        account_number = data.get("account_number")

        # Amount validation
        if amount < 300:
            return jsonify({
                "success": False,
                "message": "Minimum withdrawal amount is ৳300."
            }), 400

        if amount > 25000:
            return jsonify({
                "success": False,
                "message": "Maximum withdrawal amount is ৳25,000."
            }), 400

        # Payment method validation
        if payment_method not in ["bkash", "nagad"]:
            return jsonify({
                "success": False,
                "message": "Invalid payment method."
            }), 400

        # Account number validation
        if not account_number:
            return jsonify({
                "success": False,
                "message": "Account number is required."
            }), 400

        conn = get_connection()
        cur = conn.cursor()

        # Check current balance
        cur.execute("""
            SELECT balance
            FROM users
            WHERE id = %s
        """, (user_id,))

        user = cur.fetchone()

        if not user:
            cur.close()
            conn.close()

            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        balance = float(user["balance"])

        if amount > balance:
            cur.close()
            conn.close()

            return jsonify({
                "success": False,
                "message": "Insufficient balance."
            }), 400

        # Create withdrawal request
        cur.execute("""
            INSERT INTO withdrawals
            (user_id, amount, payment_method, account_number, status)
            VALUES (%s, %s, %s, %s, 'pending')
        """, (
            user_id,
            amount,
            payment_method,
            account_number
        ))

        # Reserve the withdrawal amount
        cur.execute("""
            UPDATE users
            SET balance = balance - %s
            WHERE id = %s
        """, (amount, user_id))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Withdraw request submitted successfully."
        }), 200

    except jwt.ExpiredSignatureError:

        return jsonify({
            "success": False,
            "message": "Token expired."
        }), 401

    except jwt.InvalidTokenError:

        return jsonify({
            "success": False,
            "message": "Invalid token."
        }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@api.route("/api/deposits", methods=["GET"])
def get_deposits():

    token = request.headers.get("Authorization")

    if not token:
        return jsonify({
            "success": False,
            "message": "Authorization token required."
        }), 401

    try:

        token = token.replace("Bearer ", "")

        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload["user_id"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                amount,
                payment_method,
                status,
                created_at
            FROM deposits
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))

        deposits = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "deposits": deposits
        }), 200

    except jwt.ExpiredSignatureError:

        return jsonify({
            "success": False,
            "message": "Token expired."
        }), 401

    except jwt.InvalidTokenError:

        return jsonify({
            "success": False,
            "message": "Invalid token."
        }), 401
    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500



@api.route("/api/withdrawals", methods=["GET"])
def get_withdrawals():

    token = request.headers.get("Authorization")

    if not token:
        return jsonify({
            "success": False,
            "message": "Authorization token required."
        }), 401

    try:

        token = token.replace("Bearer ", "")

        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload["user_id"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                amount,
                payment_method,
                status,
                created_at
            FROM withdrawals
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))

        withdrawals = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "withdrawals": withdrawals
        }), 200

    except jwt.ExpiredSignatureError:

        return jsonify({
            "success": False,
            "message": "Token expired."
        }), 401

    except jwt.InvalidTokenError:

        return jsonify({
            "success": False,
            "message": "Invalid token."
        }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
@api.route("/api/admin/withdrawals", methods=["GET"])
def admin_get_withdrawals():

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT
                id,
                user_id,
                amount,
                payment_method,
                account_number,
                status,
                created_at
            FROM withdrawals
            ORDER BY created_at DESC
        """)

        withdrawals = cur.fetchall()

        return jsonify({
            "success": True,
            "withdrawals": withdrawals
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cur.close()
        conn.close()


@api.route("/api/admin/withdraw/<int:withdrawal_id>/approve", methods=["POST"])
def approve_withdrawal(withdrawal_id):

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401

    conn = get_connection()
    cur = conn.cursor()

    try:
        # Get withdrawal information
        cur.execute("""
            SELECT status
            FROM withdrawals
            WHERE id = %s
        """, (withdrawal_id,))

        withdrawal = cur.fetchone()

        if not withdrawal:
            return jsonify({
                "success": False,
                "message": "Withdrawal not found."
            }), 404

        # Only pending withdrawals can be approved
        if withdrawal["status"] != "pending":
            return jsonify({
                "success": False,
                "message": "Withdrawal already processed."
            }), 400

        # Approve withdrawal
        cur.execute("""
            UPDATE withdrawals
            SET status = 'approved'
            WHERE id = %s
        """, (withdrawal_id,))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Withdrawal approved successfully."
        }), 200

    except Exception as e:
        conn.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cur.close()
        conn.close()
@api.route("/api/admin/withdraw/<int:withdrawal_id>/reject", methods=["POST"])
def reject_withdrawal(withdrawal_id):

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401

    conn = get_connection()
    cur = conn.cursor()
    try:
        # Get withdrawal information
        cur.execute("""
            SELECT status, amount, user_id
            FROM withdrawals
            WHERE id = %s
        """, (withdrawal_id,))

        withdrawal = cur.fetchone()

        if not withdrawal:
            return jsonify({
                "success": False,
                "message": "Withdrawal not found."
            }), 404

        # Only pending withdrawals can be rejected
        if withdrawal["status"] != "pending":
            return jsonify({
                "success": False,
                "message": "Withdrawal already processed."
            }), 400

        # Mark withdrawal as rejected
        cur.execute("""
            UPDATE withdrawals
            SET status = 'rejected'
            WHERE id = %s
        """, (withdrawal_id,))

        # Refund amount to user balance
        cur.execute("""
            UPDATE users
            SET balance = balance + %s
            WHERE id = %s
        """, (
            withdrawal["amount"],
            withdrawal["user_id"]
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Withdrawal rejected and balance refunded successfully."
        }), 200

    except Exception as e:
        conn.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        cur.close()
        conn.close()        
@api.route("/api/admin/stats", methods=["GET"])
def admin_stats():

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401

    conn = get_connection()
    cur = conn.cursor()

    # Total Users
    cur.execute("SELECT COUNT(*) AS total_users FROM users")
    total_users = cur.fetchone()["total_users"]

    # Total Balance
    cur.execute("SELECT COALESCE(SUM(balance), 0) AS total_balance FROM users")
    total_balance = cur.fetchone()["total_balance"]

    # Pending Deposits
    cur.execute(
        "SELECT COUNT(*) AS pending_deposits FROM deposits WHERE status = 'pending'"
    )
    pending_deposits = cur.fetchone()["pending_deposits"]

    # Pending Withdrawals
    cur.execute(
        "SELECT COUNT(*) AS pending_withdrawals FROM withdrawals WHERE status = 'pending'"
    )
    pending_withdrawals = cur.fetchone()["pending_withdrawals"]

    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "total_users": total_users,
        "total_balance": total_balance,
        "pending_deposits": pending_deposits,
        "pending_withdrawals": pending_withdrawals
    })
@api.route("/api/admin/users", methods=["GET"])
def admin_users():

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            username,
            email,
            balance,
            created_at
        FROM users
        ORDER BY id ASC
    """)

    users = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "users": users
    })
@api.route("/api/admin/deposits", methods=["GET"])
def admin_deposits():

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                deposits.id,
                users.username,
                deposits.amount,
                deposits.payment_method,
                deposits.transaction_id,
                deposits.status,
                deposits.created_at
            FROM deposits
            JOIN users
                ON deposits.user_id = users.id
            ORDER BY deposits.created_at DESC
        """)

        deposits = cur.fetchall()

        return jsonify({
            "success": True,
            "deposits": deposits
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cur.close()
        conn.close()
@api.route("/api/admin/deposit/<int:deposit_id>/approve", methods=["POST"])
def approve_deposit(deposit_id):

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401
    conn = get_connection()
    cur = conn.cursor()

    # Get deposit information
    cur.execute("""
        SELECT user_id, amount, status
        FROM deposits
        WHERE id = %s
    """, (deposit_id,))

    deposit = cur.fetchone()

    if not deposit:
        cur.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Deposit not found."
        }), 404

    if deposit["status"] != "pending":
        cur.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Deposit already processed."
        }), 400

    # Deposit Approve
    cur.execute("""
        UPDATE deposits
        SET status = 'approved'
        WHERE id = %s
    """, (deposit_id,))

    # User Balance Update
    cur.execute("""
        UPDATE users
        SET balance = balance + %s
        WHERE id = %s
    """, (
        deposit["amount"],
        deposit["user_id"]
    ))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Deposit approved successfully."
    })
@api.route("/api/admin/deposit/<int:deposit_id>/reject", methods=["POST"])
def reject_deposit(deposit_id):

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401

    conn = get_connection()
    cur = conn.cursor()
    # Get deposit information
    cur.execute("""
        SELECT status
        FROM deposits
        WHERE id = %s
    """, (deposit_id,))

    deposit = cur.fetchone()

    if not deposit:
        cur.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Deposit not found."
        }), 404

    if deposit["status"] != "pending":
        cur.close()
        conn.close()

        return jsonify({
            "success": False,
            "message": "Deposit already processed."
        }), 400

    cur.execute("""
        UPDATE deposits
        SET status = 'rejected'
        WHERE id = %s
    """, (deposit_id,))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Deposit rejected successfully."
    })
@api.route("/api/admin/setup", methods=["POST"])
def admin_setup():

    try:

        conn = get_connection()
        cur = conn.cursor()

        data = request.get_json() or {}

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "success": False,
                "message": "Username and password are required."
            }), 400

        # Check existing admin
        cur.execute("""
            SELECT id
            FROM admins
            WHERE username = %s
        """, (username,))

        admin = cur.fetchone()

        if admin:
            return jsonify({
                "success": False,
                "message": "Admin already exists."
            }), 400

        hashed_password = generate_password_hash(password)

        cur.execute("""
            INSERT INTO admins (username, password)
            VALUES (%s, %s)
        """, (
            username,
            hashed_password
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Admin account created successfully."
        }), 201

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cur.close()
        conn.close()
@api.route("/api/admin/login", methods=["POST"])
def admin_login():

    try:

        data = request.get_json() or {}

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "success": False,
                "message": "Username and password are required."
            }), 400

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, username, password
            FROM admins
            WHERE username = %s
        """, (username,))

        admin = cur.fetchone()

        if not admin:
            cur.close()
            conn.close()

            return jsonify({
                "success": False,
                "message": "Invalid username or password."
            }), 401

        if not check_password_hash(admin["password"], password):
            cur.close()
            conn.close()

            return jsonify({
                "success": False,
                "message": "Invalid username or password."
            }), 401

        token = jwt.encode(
            {
                "admin_id": admin["id"],
                "username": admin["username"],
                "role": "admin",
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(hours=24)
            },
            Config.SECRET_KEY,
            algorithm="HS256"
        )

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Admin login successful.",
            "token": token
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
# ===============================
# ADMIN PAYMENT SETTINGS
# ===============================

@api.route("/api/admin/payment-settings", methods=["GET"])
def get_payment_settings():

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                id,
                payment_method,
                payment_type,
                payment_number,
                usdt_network,
                usdt_address,
                is_active
            FROM payment_settings
            ORDER BY id ASC
        """)

        settings = cur.fetchall()

        return jsonify({
            "success": True,
            "settings": settings
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cur.close()
        conn.close()


@api.route("/api/admin/payment-settings", methods=["POST"])
def save_payment_settings():

    admin = verify_admin_token()

    if not admin:
        return jsonify({
            "success": False,
            "message": "Admin authorization required."
        }), 401

    data = request.get_json() or {}

    payment_method = data.get("payment_method")
    payment_type = data.get("payment_type")
    payment_number = data.get("payment_number")
    usdt_network = data.get("usdt_network")
    usdt_address = data.get("usdt_address")
    is_active = data.get("is_active", True)

    if not payment_method:
        return jsonify({
            "success": False,
            "message": "Payment method is required."
        }), 400

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            INSERT INTO payment_settings (
                payment_method,
                payment_type,
                payment_number,
                usdt_network,
                usdt_address,
                is_active,
                updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)

            ON CONFLICT (payment_method)
            DO UPDATE SET
                payment_type = EXCLUDED.payment_type,
                payment_number = EXCLUDED.payment_number,
                usdt_network = EXCLUDED.usdt_network,
                usdt_address = EXCLUDED.usdt_address,
                is_active = EXCLUDED.is_active,
                updated_at = CURRENT_TIMESTAMP
        """, (
            payment_method,
            payment_type,
            payment_number,
            usdt_network,
            usdt_address,
            is_active
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Payment settings saved successfully."
        }), 200

    except Exception as e:

        conn.rollback()

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cur.close()
        conn.close()
# ===============================
# USER PAYMENT SETTINGS
# ===============================

@api.route("/api/payment-settings", methods=["GET"])
def user_payment_settings():

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute("""
            SELECT
                payment_method,
                payment_type,
                payment_number,
                usdt_network,
                usdt_address
            FROM payment_settings
            WHERE is_active = TRUE
            ORDER BY id ASC
        """)

        settings = cur.fetchall()

        return jsonify({
            "success": True,
            "settings": settings
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:

        cur.close()
        conn.close()
# ===============================
# USER BET HISTORY
# ===============================

@api.route("/api/bet-history", methods=["GET"])
def get_bet_history():

    try:

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({
                "success": False,
                "message": "Authorization token required."
            }), 401

        token = auth_header.split(" ")[1]

        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id = payload.get("user_id")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                game,
                bet_amount,
                result,
                win_loss,
                created_at
            FROM bets
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))

        bets = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({
            "success": True,
            "bets": bets
        }), 200

    except jwt.ExpiredSignatureError:

        return jsonify({
            "success": False,
            "message": "Token expired."
        }), 401

    except jwt.InvalidTokenError:

        return jsonify({
            "success": False,
            "message": "Invalid token."
        }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500
@api.route("/api/referrals", methods=["GET"])
def get_referrals():

    conn = None
    cur = None

    try:
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Authorization token required."
            }), 401

        token = auth_header.split(" ")[1]

        try:
            decoded = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=["HS256"]
            )
        except Exception:
            return jsonify({
                "success": False,
                "message": "Invalid or expired token."
            }), 401

        user_id = decoded.get("user_id")

        if not user_id:
            user_id = decoded.get("id")

        if not user_id:
            return jsonify({
                "success": False,
                "message": "User ID not found."
            }), 401

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                r.id,
                r.referrer_id,
                r.referred_id,
                r.reward,
                r.created_at,
                u.username,
                u.email
            FROM referrals r
            JOIN users u
                ON u.id = r.referred_id
            WHERE r.referrer_id = %s
            ORDER BY r.created_at DESC
        """, (user_id,))

        referral_rows = cur.fetchall()

        referrals = []

        for row in referral_rows:

            referrals.append({
                "id": row["id"],
                "referred_id": row["referred_id"],
                "username": row["username"],
                "email": row["email"],
                "reward": float(row["reward"] or 0),
                "status": "pending",
                "created_at": row["created_at"]
            })

        return jsonify({
            "success": True,
            "referral_link":
                f"https://sharm363.github.io/CasinoPlatform/?ref={user_id}",
            "total_referrals": len(referrals),
            "referrals": referrals
        }), 200

    except Exception as e:

        if conn:
            conn.rollback()

        return jsonify({
            "success": False,
            "message": "Failed to load referrals.",
            "error": str(e)
        }), 500

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()
@api.route("/api/bet", methods=["POST"])
def place_bet():

    conn = None
    cur = None

    try:

        # Authorization
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "message": "Authorization token required."
            }), 401

        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                Config.SECRET_KEY,
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({
                "success": False,
                "message": "Token expired."
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "success": False,
                "message": "Invalid token."
            }), 401

        user_id = payload.get("user_id")

        if not user_id:
            user_id = payload.get("id")

        if not user_id:
            return jsonify({
                "success": False,
                "message": "User ID not found."
            }), 401

        data = request.get_json() or {}

        game = data.get("game")
        bet_amount = data.get("bet_amount")

        if not game or bet_amount is None:
            return jsonify({
                "success": False,
                "message": "Game and bet amount are required."
            }), 400

        try:
            bet_amount = float(bet_amount)
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Invalid bet amount."
            }), 400

        if bet_amount <= 0:
            return jsonify({
                "success": False,
                "message": "Bet amount must be greater than 0."
            }), 400

        conn = get_connection()
        cur = conn.cursor()

        # Check user balance
        cur.execute("""
            SELECT id, balance
            FROM users
            WHERE id = %s
            FOR UPDATE
        """, (user_id,))

        user = cur.fetchone()

        if not user:
            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404

        if float(user["balance"]) < bet_amount:
            return jsonify({
                "success": False,
                "message": "Insufficient balance."
            }), 400

        # Deduct bet amount
        cur.execute("""
            UPDATE users
            SET balance = balance - %s
            WHERE id = %s
        """, (bet_amount, user_id))

        # Save bet
        cur.execute("""
            INSERT INTO bets (
                user_id,
                game,
                bet_amount,
                result,
                win_loss
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (
            user_id,
            game,
            bet_amount,
            "pending",
            0
        ))

                bet = cur.fetchone()

        # Referral Bonus Check
        cur.execute("""
            SELECT
                r.id,
                r.referrer_id,
                r.deposit_requirement,
                r.turnover_requirement,
                r.bonus_paid
            FROM referrals r
            WHERE r.referred_id = %s
            AND r.bonus_paid = FALSE
            FOR UPDATE
        """, (user_id,))

        referral = cur.fetchone()

        if referral:

            # Check approved deposits
            cur.execute("""
                SELECT COALESCE(SUM(amount), 0) AS total_deposit
                FROM deposits
                WHERE user_id = %s
                AND status = 'approved'
            """, (user_id,))

            deposit_data = cur.fetchone()
            total_deposit = float(deposit_data["total_deposit"] or 0)

            # Check total turnover
            cur.execute("""
                SELECT COALESCE(SUM(bet_amount), 0) AS total_turnover
                FROM bets
                WHERE user_id = %s
            """, (user_id,))

            turnover_data = cur.fetchone()
            total_turnover = float(turnover_data["total_turnover"] or 0)

            # Both conditions completed
            if (
                total_deposit >= float(referral["deposit_requirement"])
                and total_turnover >= float(referral["turnover_requirement"])
            ):

                # Give referral bonus to referrer
                cur.execute("""
                    UPDATE users
                    SET balance = balance + 300
                    WHERE id = %s
                """, (referral["referrer_id"],))

                # Mark bonus as paid
                cur.execute("""
                    UPDATE referrals
                    SET
                        reward = 300,
                        bonus_paid = TRUE
                    WHERE id = %s
                """, (referral["id"],))

        conn.commit()

        return jsonify({
            "success": True,
            "message": "Bet placed successfully.",
            "bet": {
                "id": bet["id"],
                "game": game,
                "bet_amount": bet_amount,
                "result": "pending",
                "win_loss": 0,
                "created_at": bet["created_at"]
            }
        }), 201

    except Exception as e:
            "success": False,
            "message": "Failed to place bet.",
            "error": str(e)
        }), 500

    finally:

        if cur:
            cur.close()

        if conn:
            conn.close()
