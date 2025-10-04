from flask import Flask
from flask_cors import CORS
from ping import ping_bp
from race_info import race_info_bp
from team_standings import team_standings_bp
from driver_standings import driver_standings_bp
from flasgger import Swagger

app = Flask(__name__)
CORS(app)


app.register_blueprint(ping_bp)
app.register_blueprint(race_info_bp)
app.register_blueprint(team_standings_bp)
app.register_blueprint(driver_standings_bp)

# DEV: Swagger UI for API testing -> http://localhost:5000/apidocs/
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # include all endpoints
            "model_filter": lambda tag: True,  # include all models
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs"
}

Swagger(app, config=swagger_config)

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/")
def home():
    return "F1 Data API is running!"

# DEV: Activate virtual environment before running -> .\venv\Scripts\activate
