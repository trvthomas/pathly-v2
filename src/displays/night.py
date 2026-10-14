import random, math
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from waveshare_epd import epd7in5_V2
from src.helpers import *
from src.fonts import FONTS
from src.unhinged_sentences import get_lyrics

# Main Refresh
def refresh_display_night(data, constellation_points):
    epd = epd7in5_V2.EPD()
    epd.init()
    
    today = datetime.now()

    # Blank Screen Dashboard
    image = Image.open(f"assets/dashboard-night.bmp")
    draw = ImageDraw.Draw(image)
    
    # Today Date
    day_text = today.strftime("%a %d").upper()
    x = 28 + (5 if '1' in day_text else 0) + (5 if 'I' in day_text else 0)
    draw.text((x, 24), day_text, font=FONTS["solway-bold-small"], fill=0)

    # Statuses
    render_statuses(data["date"], image)
    
    # Modules
    display_elements = (
        module_constellation(constellation_points) +
        module_reminders(data) +
        module_tomorrow_event(data)
    )
    render_items(display_elements, draw, image)

    epd.display(epd.getbuffer(image))
    epd.sleep()

# Modules: Constellation
def module_constellation(constellation_points):
    constellation_words = ["ALPHA", "NOVA", "LYRA", "ORION", "ORBIT", "DRIFT", "ZENITH", "NEBULA", "SECTOR", "PULSE", "SOLAR", "VEGA", "AXIS", "GALAXY", "SIRIUS", "QUASAR", "NEXUS", "COSMO", "LUMEN", "AURORA"]

    # Fallback: Empty constellation PENDING
    if not constellation_points:
        return create_icon_grid([
            (120, [50, 440]),
            (300, [50, 440])
        ])

    ORIGINAL_X, ORIGINAL_Y = 25, 90
    WIDTH = 490
    HEIGHT = 280

    center_x = ORIGINAL_X + 5 + (WIDTH / 2)
    center_y = ORIGINAL_Y + 5 + (HEIGHT / 2)
    max_rx = WIDTH / 2
    max_ry = HEIGHT / 2

    const_name_suffix = random.choice(constellation_words)
    const_name_day = datetime.now().strftime("%d")
    const_name_points = len(constellation_points)
    const_name_random_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    const_name = f"{const_name_suffix}{const_name_day}-{const_name_points}{const_name_random_letter}"

    results = [{"type": "text", "x": 26, "y": 394, "content": const_name.upper(), "font_size": "solway-normal-medium"}]

    prev_coords = None
    new_constellation_points = shuffle_constellation(constellation_points)

    for p in new_constellation_points:
        angle_rad = p["angle"] * 2 * math.pi
        x_curr = center_x + (p["radius"] * max_rx * math.cos(angle_rad))
        y_curr = center_y + (p["radius"] * max_ry * math.sin(angle_rad))

        results.append({"type": "rectangle", "x": int(x_curr), "y": int(y_curr), "w": 6, "h": 6, "fill": 0})

        if prev_coords:
            results.append({"type": "line", "x1": int(prev_coords[0] + 4), "y1": int(prev_coords[1] + 4), "x2": int(x_curr + 4), "y2": int(y_curr + 4), "width": 3})
        
        prev_coords = (x_curr, y_curr)

    return results

# Modules: Reminders
def module_reminders(data):
    try:
        # Fallback: No reminders
        if not data.get("reminders"):
            sentence_lyric, sentence_song_name, sentence_artist_name = get_lyrics()

            results = [{"type": "image", "x": 565, "y": 22, "content": "song-lyric-icon"}]

            # Song lyrics
            lyric_lines = split_title_multi(sentence_lyric, 15)
            current_y = 120
            for line in lyric_lines:
                results.append({"type": "text", "x": 565, "y": current_y, "content": line, "font_size": "solway-bold-small"})
                current_y += 24
            
            # Song name
            song_name_lines = split_title_multi(sentence_song_name, 18)
            current_y = 320
            for line in reversed(song_name_lines):
                results.append({"type": "text", "x": 565, "y": current_y, "content": line, "font_size": "fredoka-normal-small"})
                current_y -= 22

            # Song artist
            results.append({"type": "text", "x": 565, "y": 345, "content": truncate_with_ellipsis(sentence_artist_name, 15), "font_size": "fredoka-bold-small"})

            # Divider line
            current_y += 14
            results.append({"type": "line", "x1": 565, "y1": current_y, "x2": 645, "y2": current_y, "width": 3})
            
            return results
        
        # List of reminders
        combined_pool = []

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

        items_to_display = combined_pool[:10]

        results = []
        current_y = 22

        for item in items_to_display:
            if item.get("icon"):
                results.append({"type": "image", "x": 556, "y": current_y + 2, "content": item["icon"]})
                
            results.append({"type": "text", "x": 580, "y": current_y, "content": truncate_with_ellipsis(item["title"], 10),  "font_size": "fredoka-normal-small"})
            results.append({"type": "text", "x": 706, "y": current_y + 5, "content": item["right_text"], "font_size": "fredoka-bold-tiny"})
            
            current_y += 35

        return results
    except Exception:
        return [
            {"type": "text", "x": 586, "y": 23, "content": ":(", "font_size": "fredoka-normal-small"}
        ]

# Modules: Tomorrow's Event
def module_tomorrow_event(data):
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    
    tomorrow_event = None
    for e in data.get("events", []):
        start_str = e.get("start", "")
        try:
            event_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            if event_dt.date() == tomorrow:
                tomorrow_event = {
                    "title": e.get("title", "No Title"),
                    "time": event_dt.strftime("%I:%M %p"),
                    "date_str": event_dt.strftime("%a %d").upper()
                }
                break
        except (ValueError, TypeError):
            continue

    # Fallback: No event tomorrow
    if not tomorrow_event:
        return create_icon_grid([
            (400, [567, 647, 727])
        ])

    # Tomorrow Event Module
    return [
        {"type": "image", "x": 567, "y": 400, "content": "module-tomorrow-event"},

        {"type": "text", "x": 630, "y": 390, "content": tomorrow_event["date_str"], "font_size": "solway-bold-small"},
        {"type": "text", "x": 630, "y": 416, "content": truncate_with_ellipsis(tomorrow_event["title"], 16), "font_size": "fredoka-normal-small"},
        {"type": "text", "x": 630, "y": 438, "content": tomorrow_event["time"], "font_size": "fredoka-normal-small"}
    ]