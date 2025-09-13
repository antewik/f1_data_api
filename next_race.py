"""Blueprint providing an API endpoint for upcoming F1 race information using FastF1 API."""

from flask import Blueprint, jsonify, Response, request
import fastf1
from datetime import datetime, timezone, timedelta, date
from typing import Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.DEBUG)

next_race_bp = Blueprint('next_race', __name__)
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


@next_race_bp.route('/nextrace')
def get_next_race() -> Response:
    """
    Get next F1 race info
    ---
    parameters:
      - name: year
        in: query
        type: integer
        required: false
        default: current year
        description: Year of the F1 season to query
    tags:
      - Race Info
    responses:
      200:
        description: Race details
    """
    fastf1.Cache.enable_cache('cache')

    now = datetime.now(timezone.utc)
    current_year = int(request.args.get("year", date.today().year))

    # Add a buffer to the race start time so the API considers the race as 'upcoming'
    # until it is likely finished. This ensures the next race is only shown after
    # the current race is over.
    RACE_DURATION = timedelta(hours=2, minutes=15)

    def find_next_race(year: int):
        schedule_df = fastf1.get_event_schedule(year)
        schedule = schedule_df.to_dict('records')

        logger.debug("Schedule DataFrame columns for %s: %s", year, schedule_df.columns)

        next_race = next(
            (
                race for race in schedule
                if race.get('Session5Date') and (race['Session5Date'] + RACE_DURATION) > now
            ),
            None
        )
        return next_race, schedule_df

    # Try current year
    try:
        next_race, schedule_df = find_next_race(current_year)
    except Exception as e:
        logger.error("Error fetching schedule for %s: %s", current_year, e)
        return jsonify({"message": "No upcoming races found."})

    # If no race left this year, look at next year
    if not next_race:
        try:
            next_race, schedule_df = find_next_race(current_year + 1)
        except Exception as e:
            logger.error("Error fetching schedule for %s: %s", current_year + 1, e)
            return jsonify({"message": "No upcoming races found."})

    if not next_race:
        return jsonify({"message": "Season finished and next season not yet available."})

    next_race_row = schedule_df[schedule_df['RoundNumber'] == next_race['RoundNumber']].iloc[0]
    event_format = next_race_row.get('EventFormat', 'standard').lower()

    response = {
        "next_race":           next_race.get('EventName', 'missing'),
        "location":            next_race.get('Location', 'missing'),
        "country":             next_race.get('Country', 'missing'),
        "official_event_name": next_race.get('OfficialEventName', 'missing'),
        "round":               next_race.get('RoundNumber', 'missing'),
        "f1_api_support":      next_race.get('F1ApiSupport', 'false'),
        "event_format":        event_format,
        "sessions": []
    }

    for i in range(1, 6):
        key = f"Session{i}"
        label = next_race_row.get(key)
        if not label:
            continue

        local_day, local_time = extract_iso_date_and_time(next_race, f"{key}Date")
        utc_day, utc_time = extract_iso_date_and_time(next_race, f"{key}DateUtc")

        response["sessions"].append({
            "name": label,
            "local": {
                "day": local_day,
                "time": local_time
            },
            "utc": {
                "day": utc_day,
                "time": utc_time
            }
        })

    return jsonify(response)
