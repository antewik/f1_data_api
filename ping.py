"""Blueprint providing a lightweight health check endpoint to confirm API availability without triggering external dependencies."""

from flask import Blueprint, jsonify

ping_bp = Blueprint('ping', __name__)

@ping_bp.route('/ping')
def ping():
    return jsonify({"status": "F1 API is awake"})
