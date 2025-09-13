from flask import Blueprint, jsonify
import fastf1
from fastf1.ergast import Ergast
import pprint

driver_standings_bp = Blueprint('driver_standings', __name__)

def extract_driver_standings(raw_response):
    """
    Return a list of driver standings dicts from a FastF1 Ergast response.
    Works with both:
      1. Old MRData JSON format
      2. New parsed list-of-dicts format
    """
    data = getattr(raw_response, 'content', raw_response)

    # New format: list of dicts with 'DriverStandings'
    if isinstance(data, list) and data:
        latest = data[-1]  # last round
        if isinstance(latest, dict) and 'DriverStandings' in latest:
            return latest['DriverStandings']

    # Old format: MRData JSON
    if isinstance(data, dict) and 'MRData' in data:
        lists = data['MRData'].get('StandingsTable', {}).get('StandingsLists', [])
        if lists:
            return lists[0].get('DriverStandings', [])

    # Unknown format
    print(f"[WARN] Unexpected Ergast format: {type(data)} -> {repr(data)[:200]}")
    return []


@driver_standings_bp.route('/driverstandings')
def get_driver_standings():
    # Enable FastF1 cache
    fastf1.Cache.enable_cache('cache')

    # Query Ergast via FastF1
    ergast = Ergast()
    raw_response = ergast.get_driver_standings(season='current', result_type='raw')

    # Extract season
    data = getattr(raw_response, 'content', raw_response)
    season = None
    if isinstance(data, list) and data:
        latest = data[-1]
        season = latest.get('season')

    # Extract standings using the hybrid helper
    standings = extract_driver_standings(raw_response)

    # Debug
    #print("DEBUG content:")
    #pprint.pprint(getattr(raw_response, 'content', raw_response))
    # if standings:
    #     print("Top-level keys in each driver entry:")
    #     pprint.pprint(list(standings[0].keys()))

    #     print("\nDriver subfields:")
    #     pprint.pprint(list(standings[0].get('Driver', {}).keys()))

    #     print("\nConstructor subfields:")
    #     constructors = standings[0].get('Constructors', [])
    #     if constructors:
    #         pprint.pprint(list(constructors[0].keys()))
    #     else:
    #         print("No constructor data found.")
    # else:
    #     print("No driver standings data available.")

    # Transform into clean JSON
    driver_list = []
    
    for entry in standings:
        driver = entry.get('Driver', {})
        constructors = entry.get('Constructors', [])
        constructor_name = constructors[0].get('name') if constructors else None
        
        driver_list.append({
            "position": int(entry.get('position', 0)),
            "points": float(entry.get('points', 0)),
            "wins": int(entry.get('wins', 0)),
            "driver_id": driver.get('driverId'),
            "given_name": driver.get('givenName'),
            "family_name": driver.get('familyName'),
            "nationality": driver.get('nationality'),
            "permanentNumber": driver.get('permanentNumber'),
            "url": driver.get('url'),
            "constructor": constructor_name
        })

    return jsonify({
        "season": season,
        "standings": driver_list
    })
