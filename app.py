from flask import Flask
from flask_cors import CORS
from ping import ping_bp
from next_race import next_race_bp
from team_standings import team_standings_bp
from driver_standings import driver_standings_bp
from flasgger import Swagger

app = Flask(__name__)
CORS(app)


app.register_blueprint(ping_bp)
app.register_blueprint(next_race_bp)
app.register_blueprint(team_standings_bp)
app.register_blueprint(driver_standings_bp)

# DEV: Swagger UI for API testing -> http://127.0.0.1:5000/apidocs
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs"
}

Swagger(app, config=swagger_config)

if __name__ == '__main__':
    app.run(debug=True)

# DEV: Activate virtual environment before running -> .\venv\Scripts\activate
