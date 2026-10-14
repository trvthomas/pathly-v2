import requests
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from waveshare_epd import epd7in5_V2
from src.helpers import *
from src.fonts import FONTS
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

# Main Refresh
def refresh_display_morning(data, general_config_today):
    epd = epd7in5_V2.EPD()
    epd.init()
    
    today = datetime.now()

    # Blank Screen Dashboard
    image = Image.open(f"assets/dashboard-morning.bmp")
    draw = ImageDraw.Draw(image)
    
    # Today Date
    draw.text((35, 22), today.strftime("%a").upper(), font=FONTS["solway-bold-medium"], fill=0)
    day_str = today.strftime("%d")
    x = 30 + (10 if "1" in day_str else 0)
    draw.text((x, 55), day_str, font=FONTS["solway-bold-huge"], fill=0)

    # Statuses
    render_statuses(data["date"], image)

    # Modules
    display_elements = (
        module_weather(general_config_today) +
        module_today_snapshot(data) +
        module_traffic(general_config_today) +
        module_events_reminders(data, general_config_today)
    )
    render_items(display_elements, draw, image)

    epd.display(epd.getbuffer(image))
    epd.sleep()

# Modules: Weather
def module_weather(general_config_today):
    coords = general_config_today['weather']['coordinates']

    url = (
        f"https://api.weatherapi.com/v1/forecast.json"
        f"?key={WEATHER_API_KEY}"
        f"&q={coords[0]},{coords[1]}"
        f"&days=1"
    )
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        max_c = data["forecast"]["forecastday"][0]["day"]["maxtemp_c"]
        max_f = round((max_c * 9/5) + 32)
        rain_chance = data["forecast"]["forecastday"][0]["day"]["daily_chance_of_rain"]
        wind_speed = data["forecast"]["forecastday"][0]["day"]["maxwind_mph"]
        weather_code = data["forecast"]["forecastday"][0]["day"]["condition"]["code"]

        units_precipitation = "%"
        units_wind = "mph"

        place_name = reverse_geocode(coords, TOMTOM_API_KEY)
        
        icon_groups = {
            "weather-sun": [1000],
            "weather-sun-clouds": [1003],
            "weather-clouds": [1006, 1009, 1135],
            "weather-rain": [1030, 1063, 1066, 1087, 1150, 1153, 1180, 1183, 1186, 1189, 1192, 1195, 1240, 1243, 1246, 1273, 1276],
            "weather-smog": [1012, 1015, 1033, 1039],
            "weather-snow": [1117]
        }
        icon = "weather-error"
        for name, codes in icon_groups.items():
            if weather_code in codes:
                icon = name
                break
        
        return [
            {"type": "image", "x": 187, "y": 28, "content": icon},
            {"type": "text", "x": 302, "y": 20, "content": f"{max_f}°", "font_size": "solway-bold-huge"},
            {"type": "text", "x": 304, "y": 90, "content": f"{max_c}°", "font_size": "solway-normal-medium"},

            {"type": "text", "x": 80, "y": 172, "content": f"{rain_chance}{units_precipitation}", "font_size": "solway-normal-medium"},
            {"type": "text", "x": 338, "y": 172, "content": f"{wind_speed} {units_wind}", "font_size": "solway-normal-medium"},

            {"type": "text", "x": 406, "y": 100, "content": truncate_with_ellipsis(place_name, 10), "font_size": "fredoka-normal-small"}
        ]
    except Exception:
        return [
            {"type": "image", "x": 187, "y": 32, "content": "weather-error"},
            {"type": "text", "x": 302, "y": 20, "content": ":(", "font_size": "solway-bold-huge"},
            
            {"type": "text", "x": 80, "y": 172, "content": "guessing", "font_size": "solway-normal-medium"},
            {"type": "text", "x": 338, "y": 172, "content": "not sure", "font_size": "solway-normal-medium"}
        ]

# Modules: Today Snapshot
def module_today_snapshot(data):
    today = datetime.now().date()

    events_count = 0
    reminders_count = 0

    try:
        for event in data.get("events", []):
            start_time = parse_event_time(event.get("start", ""))

            if start_time and start_time.date() == today:
                events_count += 1

        for reminder in data.get("reminders", []):
            due_date = datetime.strptime(reminder.get("due", ""), "%Y-%m-%d").date()

            if due_date <= today:
                reminders_count += 1
        
        return [
            {"type": "text", "x": 564, "y": 272, "content": f"{reminders_count}", "font_size": "solway-bold-huge"},
            {"type": "text", "x": 564, "y": 368, "content": f"{events_count}", "font_size": "solway-bold-huge"}
        ]
    except Exception:
        return [
            {"type": "text", "x": 564, "y": 272, "content": "-", "font_size": "solway-bold-huge"},
            {"type": "text", "x": 564, "y": 368, "content": "-", "font_size": "solway-bold-huge"}
        ]

# Modules: Traffic
def module_traffic(general_config_today):
    # Fallback: No traffic for today
    if not general_config_today.get("traffic"):
        return create_icon_grid([
            (24, [567, 647, 727]),
            (111, [567, 647, 727]),
            (198, [567, 647, 727])
        ])
    
    try:
        if general_config_today["traffic"]["type"] == "bike":
            # Traffic Module: Bike conditions
            coords = general_config_today['weather']['coordinates']
        
            url = (
                f"https://api.weatherapi.com/v1/forecast.json"
                f"?key={WEATHER_API_KEY}"
                f"&q={coords[0]},{coords[1]}"
                f"&days=1&aqi=yes"
            )
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            uv = data["forecast"]["forecastday"][0]["day"]["uv"]
            rain_chance = data["forecast"]["forecastday"][0]["day"]["daily_chance_of_rain"]
            precip_mm = data["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]
            max_wind = data["forecast"]["forecastday"][0]["day"]["maxwind_mph"]
            max_temp = data["forecast"]["forecastday"][0]["day"]["maxtemp_f"]
            min_temp = data["forecast"]["forecastday"][0]["day"]["mintemp_f"]
            aqi_data = data["current"]["air_quality"]
            
            score = 100
            advisories = []
            
            # Check rain
            if rain_chance >= 50 or precip_mm > 2.0:
                score -= 40
                advisories.append("Lots of rain")
            elif rain_chance >= 25 or precip_mm > 0.5:
                score -= 15
                advisories.append("Spotty rain likely")

            # Check wind
            if max_wind >= 22:
                score -= 25
                advisories.append("Windy day")
            elif max_wind >= 14:
                score -= 10
                advisories.append("Breezy day")

            # Check temperature and UV
            if max_temp >= 95 or uv >= 8.0:
                score -= 15
                advisories.append("Sunscreen + Water")
            elif min_temp <= 48:
                score -= 10
                advisories.append("Chilly day")

            # Check air quality
            epa_index = aqi_data.get("us-epa-index", 1)
            if epa_index >= 4:
                score -= 35
                advisories.append("Poor air quality")
            elif epa_index == 3:
                score -= 15
                advisories.append("Moderate haze")
            
            # Calculate score
            if score >= 95:
                grade = "A+"
            elif score >= 85:
                grade = "A"
            elif score >= 75:
                grade = "B"
            elif score >= 65:
                grade = "C"
            else:
                grade = "F"

            recommendation = advisories[0] if advisories else "Perfect day, enjoy!"
            
            return [
                {"type": "image", "x": 567, "y": 24, "content": "module-bike-conditions"},
                
                {"type": "text", "x": 564, "y": 134, "content": f"{grade}", "font_size": "solway-bold-huge"},
                {"type": "text", "x": 564, "y": 211, "content": recommendation, "font_size": "fredoka-normal-small"},
            ] 
        else:
            # Traffic Module: Car/Commute time
            arrive_by = datetime.now() + timedelta(minutes=80)
            arrive_at_str = arrive_by.strftime("%Y-%m-%dT%H:%M:%S")
            coords_from = general_config_today["traffic"]["coordinates_from"]
            coords_to = general_config_today["traffic"]["coordinates_to"]
            
            url = f"https://api.tomtom.com/maps/orbis/routing/routes/calculate"
            headers = {"TomTom-Api-Key": TOMTOM_API_KEY, "TomTom-Api-Version": "3", "Attributes": "routes.summary"}
            payload = {
                "routePlanningLocations": {
                    "origin": {
                        "type": "Point",
                        "coordinates": [coords_from[1], coords_from[0]],
                    },
                    "destination": {
                        "type": "Point",
                        "coordinates": [coords_to[1], coords_to[0]],
                    },
                },
                "arrivalDateTime": arrive_at_str,
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            time_travel_mins = round(data["routes"][0]["summary"]["travelDurationInSeconds"] / 60)
            place_name = reverse_geocode(coords_to, TOMTOM_API_KEY)
            
            return [
                {"type": "image", "x": 567, "y": 24, "content": "module-travel-time"},
                
                {"type": "text", "x": 564, "y": 134, "content": f"{time_travel_mins}", "font_size": "solway-bold-huge"},
                {"type": "text", "x": 638, "y": 211, "content": truncate_with_ellipsis(place_name, 12), "font_size": "fredoka-normal-small"},
            ]
    except Exception:
        return create_icon_grid([
            (24, [567, 647, 727]),
            (111, [567, 647, 727]),
            (198, [567, 647, 727])
        ])

# Modules: Events & Reminders
def module_events_reminders(data, general_config_today):
    try:
        now = datetime.now()
        today = now.date()

        # Fallback: No events or reminders for today
        today_str = now.strftime("%Y-%m-%d")
        today_events = [e for e in data.get("events", []) if e["start"].startswith(today_str)]

        if not today_events and not data.get("reminders"):
            year = now.year

            MAX_WIDTH = 460 # Max width of progress bar

            progress_semester_month_name = ""
            progress_semester_month_number = 0
            # Semester Progress
            semesters = general_config_today.get("school_semesters", {})
            for dates in semesters.items():
                start = datetime.strptime(f"{dates['start_date']}/{year}", "%m/%d/%Y").date()
                end = datetime.strptime(f"{dates['end_date']}/{year}", "%m/%d/%Y").date()
                
                if start <= today <= end:
                    progress_semester_month_name = "Semester"
                    total_days = (end - start).days
                    elapsed_days = (today - start).days
                    progress_semester_month_number = int((elapsed_days / total_days) * 100)
                    break
            
            if not progress_semester_month_name:
                progress_semester_month_name = now.strftime("%B")
                day_of_month = now.day
                next_month = now.replace(day=28) + timedelta(days=4)
                last_day_of_month = (next_month - timedelta(days=next_month.day)).day
                progress_semester_month_number = int((day_of_month / last_day_of_month) * 100)
            
            fill_width_semester_month = int((progress_semester_month_number / 100) * MAX_WIDTH)

            # Year Progress
            day_of_year = int(now.strftime("%j"))
            progress_year = int((day_of_year / 365) * 100)
            fill_width_year = int((progress_year / 100) * MAX_WIDTH)
            
            return [
                {"type": "image", "x": 23, "y": 280, "content": "module-progress"},

                {"type": "text", "x": 38, "y": 290, "content": f"{progress_semester_month_name} Progress", "font_size": "fredoka-normal-small"},
                {"type": "text", "x": 453, "y": 291, "content": f"{progress_semester_month_number}%", "font_size": "solway-normal-small"},
                {"type": "rectangle", "x": 52, "y": 325, "w": fill_width_semester_month, "h": 26, "fill": 0},

                {"type": "text", "x": 453, "y": 375, "content": f"{progress_year}%", "font_size": "solway-normal-small"},
                {"type": "rectangle", "x": 52, "y": 406, "w": fill_width_year, "h": 26, "fill": 0}
            ]
        
        # Events and Reminders Module
        combined_pool = []
        morning_time = datetime.combine(today, datetime.strptime(general_config_today["refresh"]["morning"], "%H:%M").time())

        for event in data.get("events", []):
            start_time = parse_event_time(event.get("start", ""))
            if start_time and start_time.date() == today and start_time < morning_time:
                combined_pool.append({
                    "sort_key": 1,
                    "time_sort": start_time,
                    "icon": event.get("icon", "calendar-default"),
                    "title": event.get("title", "Error in retrieving event"),
                    "right_text": start_time.strftime("%I:%M %p")
                })

        for task in data.get("reminders", []):
            is_flagged = task.get("flagged", False)
            due_str = task.get("due", "")
            try:
                due_date = datetime.strptime(due_str, "%Y-%m-%d").replace(hour=23, minute=59)
            except (ValueError, TypeError):
                due_date = datetime.max

            combined_pool.append({
                "sort_key": 2 if is_flagged else 3, 
                "time_sort": due_date,
                "icon": "reminder-flag" if is_flagged else "default-task",
                "title": task.get("title", "Error in retrieving task"),
                "right_text": format_due_date(due_str)
            })

        combined_pool.sort(key=lambda x: (x["sort_key"], x["time_sort"]))

        items_to_display = combined_pool[:5]

        results = []
        current_y = 288

        for item in items_to_display:
            if item.get("icon"):
                results.append({"type": "image", "x": 23, "y": current_y + 2, "content": item["icon"]})
                
            results.append({"type": "text", "x": 49, "y": current_y, "content": truncate_with_ellipsis(item["title"], 30), "font_size": "fredoka-normal-small"})
            results.append({"type": "text", "x": 425, "y": current_y, "content": item["right_text"], "font_size": "fredoka-bold-small"})
            
            current_y += 35

        return results
    except Exception:
        return create_icon_grid([
            (280, [23, 136, 249, 362, 475]),
            (340, [79, 192, 305, 418]),
            (400, [23, 136, 249, 362, 475])
        ])