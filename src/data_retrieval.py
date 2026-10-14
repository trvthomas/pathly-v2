import os, requests, json, re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TASKS_JSON_URL = os.getenv("TASKS_JSON_URL")
LYRICS_JSON_URL = os.getenv("LYRICS_JSON_URL")

DATA_FILE = 'data/data.json'
LYRICS_FILE = 'data/lyrics.json'
DAY_CONFIG_FILE = 'data/day_config.json'

KEYWORD_TO_ICON = {
    "gym": "calendar-dumbbell",
    "reading": "calendar-book",
    "work": "calendar-briefcase",
    "club": "calendar-people-group",
    "swimming": "calendar-swimming"
}

def fetch_events_reminders():
    try:
        res = requests.get(TASKS_JSON_URL)
        res.raise_for_status()
        
        txt = res.text.lstrip('\ufeff').strip()
        txt = re.sub(r',(\s*[\]}])', r'\1', txt)

        data = json.loads(txt)

        for event in data.get("events", []):
            event["title"] = clean_text(event.get("title", ""))
            event["icon"] = assign_icon(event.get("title", ""))

        for reminder in data.get("reminders", []):
            reminder["title"] = clean_text(reminder.get("title", ""))

        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        update_config({'last_fetched': datetime.now().isoformat(), 'error_retrieval': False})
    except Exception:
        update_config({'error_retrieval': True})

def fetch_lyrics():
    if not LYRICS_JSON_URL:
        update_config({'last_fetched_lyrics': datetime.now().isoformat(), 'error_retrieval_lyrics': False})
        return
    
    try:
        res = requests.get(LYRICS_JSON_URL)
        res.raise_for_status()
        
        txt = res.text.lstrip('\ufeff').strip()
        txt = re.sub(r',(\s*[\]}])', r'\1', txt)

        data = json.loads(txt)

        for item in data:
            item['lyric'] = clean_text(item['lyric'])
            item['song'] = clean_text(item['song'])
            item['artist'] = clean_text(item['artist'])

        with open(LYRICS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        update_config({'last_fetched_lyrics': datetime.now().isoformat(), 'error_retrieval_lyrics': False})
    except Exception:
        update_config({'error_retrieval_lyrics': True})

def update_config(updates):
    config = {}
    if os.path.exists(DAY_CONFIG_FILE):
        try:
            with open(DAY_CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {}

    config.update(updates)

    with open(DAY_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def assign_icon(title):
    lowered = title.lower()
    for keyword, icon in KEYWORD_TO_ICON.items():
        if keyword in lowered:
            return icon
    return "calendar-default"

def clean_text(text):
    return text.replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2026', '...')