from flask import Flask
from routes import api

app = Flask(__name__)

# Register API Blueprint
app.register_blueprint(api)


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
