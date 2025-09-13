from flask import Blueprint, jsonify
import fastf1
from datetime import datetime, timezone, timedelta
import pprint

race_info_bp = Blueprint('race_info', __name__)

@race_info_bp.route('/raceinfo')
def get_f1_info():
    fastf1.Cache.enable_cache('cache')

    # Define these inside the function
    schedule_df = fastf1.get_event_schedule(2025)
    schedule = schedule_df.to_dict('records')

    #print("DEBUG columns:")
    #print(schedule_df.columns)
    #print("DEBUG content:")
    #pprint.pprint(schedule)

    now = datetime.now(timezone.utc)
    RACE_DURATION = timedelta(hours=2, minutes=15)

    next_race = next(
        (
            race for race in schedule
            if race.get('Session5Date') and (race['Session5Date'] + RACE_DURATION) > now
        ),
        None
    )

    def format_session(date):
        return date.isoformat() if date else None

    if next_race:
        # Separate Date and Time for practice 1-4, qualifying and race - local time
        practice1_day, practice1_time = extract_iso_date_time(next_race, 'Session1Date')
        practice2_day, practice2_time = extract_iso_date_time(next_race, 'Session2Date')
        practice3_day, practice3_time = extract_iso_date_time(next_race, 'Session3Date')
        qualifying_day, qualifying_time = extract_iso_date_time(next_race, 'Session4Date')
        race_day, race_time = extract_iso_date_time(next_race, 'Session5Date')
        
        # Separate Date and Time for practice 1-4, qualifying and race - UTC time
        practice1_day_utc, practice1_time_utc = extract_iso_date_time(next_race, 'Session1DateUtc')
        practice2_day_utc, practice2_time_utc = extract_iso_date_time(next_race, 'Session2DateUtc')
        practice3_day_utc, practice3_time_utc = extract_iso_date_time(next_race, 'Session3DateUtc')
        qualifying_day_utc, qualifying_time_utc = extract_iso_date_time(next_race, 'Session4DateUtc')
        race_day_utc, race_time_utc = extract_iso_date_time(next_race, 'Session5DateUtc')
        

        return jsonify({
            "next_race": next_race.get('EventName', 'missing'),
            "location": next_race.get('Location', 'missing'),
            "country": next_race.get('Country', 'missing'),
            "official_event_name": next_race.get('OfficialEventName', 'missing'),
            "round": next_race.get('RoundNumber', 'missing'),
            "f1_api_support": next_race.get('F1ApiSupport', 'false'),
            "practice1_day": practice1_day,
            "practice1_day_utc": practice1_day_utc,
            "practice1_time": practice1_time,
            "practice1_time_utc": practice1_time_utc,
            "practice2_day": practice2_day,
            "practice2_day_utc": practice2_day_utc,
            "practice2_time_": practice2_time,
            "practice2_time_utc": practice2_time_utc,
            "practice3_day": practice3_day,
            "practice3_day_utc": practice3_day_utc,
            "practice3_time": practice3_time,
            "practice3_time_utc": practice3_time_utc,
            "qualifying_day": qualifying_day,
            "qualifying_day_utc": qualifying_day_utc,
            "qualifying_time": qualifying_time,
            "qualifying_time_utc": qualifying_time_utc,
            "race_day": race_day,
            "race_day_utc": race_day_utc,
            "race_time": race_time,
            "race_time_utc": race_time_utc
        })
    else:
        return jsonify({"message": "No upcoming races found."})


def extract_iso_date_time(race_data, session_key):
    dt = race_data.get(session_key)
    if dt:
        return dt.date().isoformat(), dt.time().isoformat()
    return None, None
