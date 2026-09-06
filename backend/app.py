from flask import Flask
from routes import api
from database import init_db

app = Flask(__name__)

# Register API Blueprint
app.register_blueprint(api)

# Initialize database tables
init_db()


@app.route("/")
def home():
    return {
        "success": True,
        "name": "CasinoPlatform API",
        "version": "1.0.0",
        "status": "Running"
    }


if __name__ == "__main__":
    app.run(debug=True)
