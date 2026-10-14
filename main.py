import os, json, time
from datetime import datetime, timedelta
from src.data_retrieval import fetch_events_reminders, fetch_lyrics
from src.refresh_eink import refresh_eink_display
from src.data_parser import load_data
from src.helpers import parse_event_time
from src.displays.welcome_error import refresh_display_fatal_error, refresh_display_welcome
from src.data_retrieval import update_config

DAY_CONFIG_FILE = "data/day_config.json"
GENERAL_CONFIG_FILE = "data/general_config.json"

def pathly_loop():
    while True:
        if not os.path.exists(DAY_CONFIG_FILE):
            refresh_display_fatal_error()
            break
    
        with open(DAY_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            intro_shown = config.get("intro_shown")

        if not intro_shown:
            refresh_display_welcome()
            update_config({'intro_shown': True})
            time.sleep(120)

        if should_fetch_events_reminders():
            fetch_events_reminders()
            time.sleep(5)
        
        if should_fetch_lyrics():
            fetch_lyrics()
            time.sleep(5)
        
        tasks_events_data = load_data()
        today_general_config = get_general_config_today()
        
        refresh_eink_display(tasks_events_data, today_general_config)

        # Calculate Sleep
        next_time = get_next_trigger_time(tasks_events_data, today_general_config)
        sleep_seconds = (next_time - datetime.now()).total_seconds()
        
        if sleep_seconds > 0:
            time.sleep(sleep_seconds + 2)
        else:
            time.sleep(120)

# Get current day refresh info
def get_general_config_today():
    with open(GENERAL_CONFIG_FILE, 'r') as f:
        general_config = json.load(f)
    
    day_name = datetime.now().strftime("%a")
    return {
        "refresh": general_config["refresh"].get(day_name),
        "weather": general_config["weather"].get(day_name),
        "traffic": general_config["traffic"].get(day_name),
        "semesters": general_config["school_semesters"]
    }

def get_next_trigger_time(data, general_config_today):
    now = datetime.now()
    today = now.date()

    search_dates = [today, today + timedelta(days=1)]
    triggers = []

    for day in search_dates:
        # 6:00 AM
        triggers.append(datetime.combine(day, datetime.strptime("06:00", "%H:%M").time()))
        
        # Morning/Night refresh
        morning_time = datetime.combine(day, datetime.strptime(general_config_today["refresh"]["morning"], "%H:%M").time())
        night_time = datetime.combine(day, datetime.strptime(general_config_today["refresh"]["night"], "%H:%M").time())
        triggers.append(morning_time)
        triggers.append(night_time)

        # 1hr 30min before first event
        day_events = [
            e for e in data.get("events", [])
            if (p_time := parse_event_time(e.get("start", ""))) and p_time.date() == day
        ]
        if day_events:
            sorted_ev = sorted(day_events, key=lambda x: x.get("start", ""))
            first_event_time = parse_event_time(sorted_ev[0].get("start", ""))
            seven_am = datetime.combine(day, datetime.strptime("07:00", "%H:%M").time())
            
            if seven_am <= first_event_time < morning_time:
                triggers.append(first_event_time - timedelta(minutes=90))

        # Hourly refresh
        curr = morning_time + timedelta(hours=1)
        while curr < night_time:
            triggers.append(curr)
            curr += timedelta(hours=1)


    future_triggers = [t for t in triggers if t > (now + timedelta(seconds=1))]
    next_time = min(future_triggers)
    return next_time

def should_fetch_events_reminders():
    if not os.path.exists(DAY_CONFIG_FILE):
        return True

    with open(DAY_CONFIG_FILE, 'r') as f:
        config = json.load(f)
        last_fetched_str = config.get("last_fetched")

    if not last_fetched_str:
        return True

    try:
        last_fetched = datetime.fromisoformat(last_fetched_str)
    except:
        return True

    return (datetime.now() - last_fetched).total_seconds() > 4 * 3600 # 4 hours

def should_fetch_lyrics():
    if not os.path.exists(DAY_CONFIG_FILE):
        return True

    with open(DAY_CONFIG_FILE, 'r') as f:
        config = json.load(f)
        last_fetched_str = config.get("last_fetched_lyrics")

    if not last_fetched_str:
        return True

    try:
        last_fetched = datetime.fromisoformat(last_fetched_str)
    except:
        return True

    return (datetime.now() - last_fetched).total_seconds() > 14 * 24 * 3600 # 2 weeks

if __name__ == "__main__":
    pathly_loop()