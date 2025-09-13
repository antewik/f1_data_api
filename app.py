from flask import Flask
from flask_cors import CORS
from race_info import race_info_bp
from team_standings import team_standings_bp
from driver_standings import driver_standings_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(race_info_bp)
app.register_blueprint(team_standings_bp)
app.register_blueprint(driver_standings_bp)

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/")
def home():
    return "F1 Data API is running!"
