"""Blueprint providing an API endpoint for upcoming F1 race information using FastF1 API."""

from flask import Blueprint, jsonify, Response, request
import fastf1
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Tuple
import logging
logging.basicConfig(level=logging.DEBUG)

race_info_bp = Blueprint('race_info', __name__)

logger = logging.getLogger(__name__)

def extract_iso_date_and_time(
    race_data: dict[str, Any], 
    session_key: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Extracts the ISO date and time strings from a datetime object in race_data.

    Args:
        race_data: Dictionary containing race session data.
        session_key: The key for the session datetime.

    Returns:
        A tuple (date_str, time_str) in ISO format, or (None, None) if not available.
    """
    dt = race_data.get(session_key)
    if dt:
        return dt.date().isoformat(), dt.time().isoformat()
    return None, None


@race_info_bp.route('/raceinfo')
def get_f1_info() -> Response:
    """
    Get next F1 race info
    ---
    parameters:
      - name: year
        in: query
        type: integer
        required: false
        default: 2025
        description: Year of the F1 season to query
    tags:
      - Race Info
    responses:
      200:
        description: Race details
    """
    
    fastf1.Cache.enable_cache('cache')

    year = int(request.args.get("year", 2025))
    schedule_df = fastf1.get_event_schedule(year)
    schedule = schedule_df.to_dict('records')

    logger.debug("Schedule DataFrame columns: %s", schedule_df.columns)

    now = datetime.now(timezone.utc)

    # Add a buffer to the race start time so the API considers the race as 'upcoming'
    # until it is likely finished. This ensures the next race is only shown after
    # the current race is over.
    RACE_DURATION = timedelta(hours=2, minutes=15)

    next_race = next(
        (
            race for race in schedule
            if race.get('Session5Date') and (race['Session5Date'] + RACE_DURATION) > now
        ),
        None
    )

    if not next_race:
        return jsonify({"message": "No upcoming races found."})

    # Separate Date and Time for practice 1-4, qualifying and race - local time
    practice1_day, practice1_time = extract_iso_date_and_time(next_race, 'Session1Date')
    practice2_day, practice2_time = extract_iso_date_and_time(next_race, 'Session2Date')
    practice3_day, practice3_time = extract_iso_date_and_time(next_race, 'Session3Date')
    qualifying_day, qualifying_time = extract_iso_date_and_time(next_race, 'Session4Date')
    race_day, race_time = extract_iso_date_and_time(next_race, 'Session5Date')
        
    # Separate Date and Time for practice 1-4, qualifying and race - UTC time
    practice1_day_utc, practice1_time_utc = extract_iso_date_and_time(next_race, 'Session1DateUtc')
    practice2_day_utc, practice2_time_utc = extract_iso_date_and_time(next_race, 'Session2DateUtc')
    practice3_day_utc, practice3_time_utc = extract_iso_date_and_time(next_race, 'Session3DateUtc')
    qualifying_day_utc, qualifying_time_utc = extract_iso_date_and_time(next_race, 'Session4DateUtc')
    race_day_utc, race_time_utc = extract_iso_date_and_time(next_race, 'Session5DateUtc')
        

    return jsonify({
        "next_race":           next_race.get('EventName', 'missing'),
        "location":            next_race.get('Location', 'missing'),
        "country":             next_race.get('Country', 'missing'),
        "official_event_name": next_race.get('OfficialEventName', 'missing'),
        "round":               next_race.get('RoundNumber', 'missing'),
        "f1_api_support":      next_race.get('F1ApiSupport', 'false'),
        "practice1_day":       practice1_day,
        "practice1_day_utc":   practice1_day_utc,
        "practice1_time":      practice1_time,
        "practice1_time_utc":  practice1_time_utc,
        "practice2_day":       practice2_day,
        "practice2_day_utc":   practice2_day_utc,
        "practice2_time":      practice2_time,
        "practice2_time_utc":  practice2_time_utc,
        "practice3_day":       practice3_day,
        "practice3_day_utc":   practice3_day_utc,
        "practice3_time":      practice3_time,
        "practice3_time_utc":  practice3_time_utc,
        "qualifying_day":      qualifying_day,
        "qualifying_day_utc":  qualifying_day_utc,
        "qualifying_time":     qualifying_time,
        "qualifying_time_utc": qualifying_time_utc,
        "race_day":            race_day,
        "race_day_utc":        race_day_utc,
        "race_time":           race_time,
        "race_time_utc":       race_time_utc
    })
