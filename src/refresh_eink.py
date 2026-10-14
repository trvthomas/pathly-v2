import json, random
from datetime import datetime
from src.displays.morning import refresh_display_morning
from src.displays.day import refresh_display_default
from src.displays.night import refresh_display_night

DAY_CONFIG = "data/day_config.json"

def refresh_eink_display(data, general_config_today):
    now = datetime.now()
    today_date = now.date()
    
    with open(DAY_CONFIG, 'r') as f:
        day_state = json.load(f)

    # 6:00 AM: Reset
    if now.hour == 6 and now.minute < 5:
        day_state["constellation_points"] = []
        save_state(day_state)

    morning_time = datetime.combine(today_date, datetime.strptime(general_config_today["refresh"]["morning"], "%H:%M").time())
    night_time = datetime.combine(today_date, datetime.strptime(general_config_today["refresh"]["night"], "%H:%M").time())

    # Morning Screen
    if now < morning_time:
        refresh_display_morning(data, general_config_today)

    # Day Screen
    elif morning_time <= now < night_time:
        current_hour = now.strftime("%H")
        constellation_already_added = False

        if day_state["constellation_points"]:
            last_point = day_state["constellation_points"][-1]
            if last_point["time"].startswith(current_hour):
                constellation_already_added = True

        if not constellation_already_added:
            new_point = generate_constellation_point(morning_time, night_time)
            day_state["constellation_points"].append(new_point)
        
        should_draw = False
        if general_config_today["refresh"].get("hourly"): # Hourly Refresh
            should_draw = True
        else: # 3-hour Refresh
            last_ref = datetime.fromisoformat(day_state.get("last_display_refresh", now.isoformat()))
            if (now - last_ref).total_seconds() >= 3 * 3600:
                should_draw = True

        if should_draw:
            refresh_display_default(data, day_state["constellation_points"])
            day_state["last_display_refresh"] = now.isoformat()
        
        save_state(day_state)

    # Night Screen
    else:
        refresh_display_night(data, day_state["constellation_points"])

def generate_constellation_point(start_time, end_time):
    now = datetime.now()
    total_seconds = (end_time - start_time).total_seconds()
    elapsed_seconds = (now - start_time).total_seconds()

    angle_norm = (elapsed_seconds / total_seconds) % 1.0
    angle_norm = (angle_norm + random.uniform(-0.01, 0.01)) % 1.0
    radius_norm = random.uniform(0.3, 0.9)
    
    return {"angle": round(angle_norm, 4), "radius": round(radius_norm, 4), "time": now.strftime("%H:%M")}

def save_state(state):
    with open(DAY_CONFIG, 'w') as f:
        json.dump(state, f, indent=4)