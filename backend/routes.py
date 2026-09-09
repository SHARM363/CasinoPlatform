from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection
from config import Config
import jwt
import datetime

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
