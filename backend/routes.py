from flask import Blueprint, jsonify

api = Blueprint("api", __name__)

@api.route("/api")
def api_home():
    return jsonify({
        "success": True,
        "message": "CasinoPlatform API is working"
    })
