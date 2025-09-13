from flask import Blueprint, jsonify
import fastf1
from fastf1.ergast import Ergast
import pprint

team_standings_bp = Blueprint('team_standings', __name__)

def extract_constructor_standings(raw_response):
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
    print(f"[WARN] Unexpected Ergast format: {type(data)} -> {repr(data)[:200]}")
    return []


@team_standings_bp.route('/teamstandings')
def get_team_standings():
    fastf1.Cache.enable_cache('cache')

    ergast = Ergast()
    raw_response = ergast.get_constructor_standings(season='current', result_type='raw')
    
    standings = extract_constructor_standings(raw_response)

    # Debug
    # print("DEBUG content:")
    # pprint.pprint(getattr(raw_response, 'content', raw_response))

    # if standings:
    #     print("Available columns in constructor standings:")
    #     print(list(standings[0].keys()))
    #     print("Constructor subfields:")
    #     print(list(standings[0].get('Constructor', {}).keys()))
    # else:
    #     print("No standings data found.")

    team_list = []
    for entry in standings:
        constructor = entry.get('Constructor', {})

        team_list.append({
            "position": int(entry.get('position', 0)),
            "points": float(entry.get('points', 0)),
            "wins": int(entry.get('wins', 0)),
            "constructor_id": constructor.get('constructorId'),
            "name": constructor.get('name'),
            "nationality": constructor.get('nationality'),
            "url": constructor.get('url')
        })

    return jsonify(team_list)
