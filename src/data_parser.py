import os, json
from datetime import datetime
from src.helpers import parse_event_time

DATA_FILE = 'data/data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "date": None,
            "events": [],
            "reminders": []
        }
    
    with open(DATA_FILE, 'r') as f:
        try:
            raw = json.load(f)
            return {
                "date": raw.get("date"),
                "events": parse_events(raw.get("events", [])),
                "reminders": parse_reminders(raw.get("reminders", []))
            }
        except json.JSONDecodeError:
            return {
                "date": None,
                "events": [],
                "reminders": []
            }

# Sort events by start date/time
def parse_events(events):
    now = datetime.now()
    
    future_events = []
    for e in events:
        end_str = e.get("end") or e.get("start", "")
        end_time = parse_event_time(end_str)
        
        if end_time and end_time > now:
            future_events.append(e)

    sorted_events = sorted(future_events, key=lambda x: x.get("start", ""))
    return sorted_events

# Sort reminders by flagged status and due date
def parse_reminders(reminders):
    sorted_reminders = sorted(reminders, key=lambda x: (not x.get("flagged", False), x.get("due", "")))
    return sorted_reminders