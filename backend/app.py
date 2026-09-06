from flask import Flask

app = Flask(__name__)

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
