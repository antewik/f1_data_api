"""Blueprint providing an API endpoint for current F1 constructor standings using FastF1 Ergast."""

from flask import Blueprint, jsonify, Response
import fastf1
from fastf1.ergast import Ergast
from typing import Any, List, Dict
import logging
logging.basicConfig(level=logging.DEBUG)

team_standings_bp = Blueprint('team_standings', __name__)

logger = logging.getLogger(__name__)

def extract_constructor_standings(raw_response: Any) -> List[Dict[str, Any]]:
    """
    Return a list of constructor standings dicts from a FastF1 Ergast response.
    Works with both:
      1. Old MRData JSON format
      2. New parsed list-of-dicts format
    """
    data = getattr(raw_response, 'content', raw_response)

    # New format: list of dicts with 'ConstructorStandings'
    if isinstance(data, list) and data:
        latest = data[-1]  # last round
        if isinstance(latest, dict) and 'ConstructorStandings' in latest:
            return latest['ConstructorStandings']

    # Old format: MRData JSON
    if isinstance(data, dict) and 'MRData' in data:
        lists = data['MRData'].get('StandingsTable', {}).get('StandingsLists', [])
        if lists:
            return lists[0].get('ConstructorStandings', [])

    # Unknown format
    logger.warning("Unexpected Ergast format: %s -> %s", type(data), repr(data)[:200])
    return []


@team_standings_bp.route('/teamstandings')
def get_team_standings() -> Response:
    """
    Get current F1 constructor standings
    ---
    tags:
      - Team Standings
    responses:
      200:
        description: JSON array containing constructor standings for the current season
    """

    fastf1.Cache.enable_cache('cache')

    ergast = Ergast()
    raw_response = ergast.get_constructor_standings(season='current', result_type='raw')    
    standings = extract_constructor_standings(raw_response)

    # Debug: log available fields/columns in the response
    data = getattr(raw_response, 'content', raw_response)
    logger.debug("Raw response content keys: %s", list(data[0].keys()) if isinstance(data, list) and data else list(data.keys()) if isinstance(data, dict) else type(data))

    if standings:
        logger.debug("Available columns in constructor standings: %s", list(standings[0].keys()))
        logger.debug("Constructor subfields: %s", list(standings[0].get('Constructor', {}).keys()))
    else:
        logger.debug("No standings data found.")

    team_list = []
    for entry in standings:
        constructor = entry.get('Constructor', {})

        team_list.append({
            "position":       int(entry.get('position', 0)),
            "points":         float(entry.get('points', 0)),
            "wins":           int(entry.get('wins', 0)),
            "constructor_id": constructor.get('constructorId'),
            "name":           constructor.get('name'),
            "nationality":    constructor.get('nationality'),
            "url":            constructor.get('url')
        })

    return jsonify(team_list)
