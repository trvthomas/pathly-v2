import math
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from waveshare_epd import epd7in5_V2
from src.helpers import *
from src.fonts import FONTS
from src.unhinged_sentences import get_day_vibe, get_fact

# Main Refresh
def refresh_display_default(data, constellation_points):
    epd = epd7in5_V2.EPD()
    epd.init()
    
    today = datetime.now()

    # Blank Screen Dashboard
    image = Image.open(f"assets/dashboard-day.bmp")
    draw = ImageDraw.Draw(image)
    
    # Today Date
    day_text = today.strftime("%a %d").upper()
    x = 28 + (5 if '1' in day_text else 0) + (5 if 'I' in day_text else 0)
    draw.text((x, 24), day_text, font=FONTS["solway-bold-small"], fill=0)

    # Statuses
    render_statuses(data["date"], image)
    
    # Modules
    display_elements = (
        module_events_reminders(data) +
        module_top_priority(data) +
        module_countdown_overdue(data) +
        module_constellation(constellation_points)
    )
    render_items(display_elements, draw, image)

    epd.display(epd.getbuffer(image))
    epd.sleep()

# Modules: Events & Reminders
def module_events_reminders(data):
    try:
        now = datetime.now()
        today = now.date()

        # Fallback: No events or reminders for today
        today_str = now.strftime("%Y-%m-%d")
        today_events = [e for e in data.get("events", []) if e["start"].startswith(today_str)]

        if not today_events and not data.get("reminders"):
            sentence_day_vibe = get_day_vibe()
            sentence_fact = get_fact(now)

            results = []

            day_vibe_lines = split_title_multi(sentence_day_vibe, 12)
            current_y = 90
            for line in day_vibe_lines:
                results.append({"type": "text", "x": 23, "y": current_y, "content": line, "font_size": "solway-bold-huge"})
                current_y += 57
            
            current_y += 40
            
            fact_lines = split_title_multi(sentence_fact, 24)
            for line in fact_lines:
                results.append({"type": "text", "x": 23, "y": current_y, "content": line, "font_size": "solway-bold-medium"})
                current_y += 40
            
            return results

        # List of Events and Reminders
        combined_pool = []

        # Events
        for e in data.get("events", []):
            start_time = parse_event_time(e.get("start", ""))

            if start_time and start_time.date() == today:
                combined_pool.append({
                    "sort_key": 1,
                    "time_sort": start_time,
                    "icon": e.get("icon", "calendar-default"),
                    "title": e.get("title", "Error in retrieving event"),
                    "right_text": start_time.strftime("%I:%M %p")
                })

        # Tasks
        for t in data.get("reminders", []):
            is_flagged = t.get("flagged", False)
            due_str = t.get("due", "")
            try:
                due_date = datetime.strptime(due_str, "%Y-%m-%d").replace(hour=23, minute=59)
            except (ValueError, TypeError):
                due_date = datetime.max

            combined_pool.append({
                "sort_key": 2 if is_flagged else 3, 
                "time_sort": due_date,
                "icon": "reminder-flag" if is_flagged else "default-task",
                "title": t.get("title", "Error in retrieving task"),
                "right_text": format_due_date(due_str)
            })

        combined_pool.sort(key=lambda x: (x["sort_key"], x["time_sort"]))

        items_to_display = combined_pool[:12]

        results = []
        current_y = 90

        for item in items_to_display:
            if item.get("icon"):
                results.append({"type": "image", "x": 23, "y": current_y + 2, "content": item["icon"]})
                
            results.append({"type": "text", "x": 49, "y": current_y, "content": truncate_with_ellipsis(item["title"], 30),  "font_size": "fredoka-normal-small"})
            results.append({"type": "text", "x": 425, "y": current_y, "content": item["right_text"], "font_size": "fredoka-bold-small"})

            current_y += 35

        return results
    except Exception:
        return [
            {"type": "text", "x": 49, "y": 88, "content": ":(", "font_size": "fredoka-normal-small"}
        ]

# Modules: Top Priority/Tasks for...
def module_top_priority(data):
    now = datetime.now()
    flagged_tasks = [t for t in data.get("reminders", []) if t.get("flagged")]
    
    # Fallback: No tasks, show Tasks Load
    if not flagged_tasks:
        today = now.date()
        tomorrow = today + timedelta(days=1)
        
        counts = {"today": 0, "tomorrow": 0, "future": 0}

        for t in data.get("reminders", []):
            due_str = t.get("due", "")
            if not due_str:
                counts["future"] += 1
                continue

            try:
                due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
                if due_date <= today:
                    counts["today"] += 1
                elif due_date == tomorrow:
                    counts["tomorrow"] += 1
                else:
                    counts["future"] += 1
            except ValueError:
                counts["future"] += 1
        
        MAX_HEIGHT = 72
        BASE_Y = 152

        progress_today = int((min(counts["today"], 10) / 10) * 100)
        fill_height_today = int((progress_today / 100) * MAX_HEIGHT)
        
        progress_tomorrow = int((min(counts["tomorrow"], 10) / 10) * 100)
        fill_height_tomorrow = int((progress_tomorrow / 100) * MAX_HEIGHT)
        
        progress_future = int((min(counts["future"], 10) / 10) * 100)
        fill_height_future = int((progress_future / 100) * MAX_HEIGHT)

        return [
            {"type": "image", "x": 567, "y": 24, "content": "module-tasks-load"},

            {"type": "rectangle", "x": 579, "y": BASE_Y - fill_height_today, "w": 20, "h": fill_height_today, "fill": 0},
            {"type": "text", "x": 582, "y": 55, "content": str(counts["today"]) if counts["today"] < 10 else "+", "font_size": "fredoka-normal-small"},
            {"type": "rectangle", "x": 660, "y": BASE_Y - fill_height_tomorrow, "w": 20, "h": fill_height_tomorrow, "fill": 0},
            {"type": "text", "x": 663, "y": 55, "content": str(counts["tomorrow"]) if counts["tomorrow"] < 10 else "+", "font_size": "fredoka-normal-small"},

            {"type": "rectangle", "x": 741, "y": BASE_Y - fill_height_future, "w": 20, "h": fill_height_future, "fill": 0},
            {"type": "text", "x": 744, "y": 55, "content": str(counts["future"]) if counts["future"] < 10 else "+", "font_size": "fredoka-normal-small"}
        ]
    
    # Top Priority Module
    top_task = min(flagged_tasks, key=lambda x: x.get("due") or "9999-12-31")
    due_str = top_task.get("due", "")

    title_lines = split_title(top_task.get("title", ":("), 10)

    results = [
        {"type": "image", "x": 570, "y": 24, "content": "module-top-priority"},
    ]

    current_y = 82
    for line in title_lines:
        results.append({"type": "text", "x": 630, "y": current_y, "content": line, "font_size": "fredoka-normal-small"})
        current_y += 22

    results.append({"type": "text", "x": 570, "y": 144, "content": f"Due {format_due_date(due_str)}", "font_size": "fredoka-bold-small"})

    return results

# Modules: Exam Countdown/Overdue Tasks
def module_countdown_overdue(data):
    today = datetime.now().date()
    all_items = data.get("events", []) + data.get("reminders", [])
    keywords = ["test", "exam"]

    future_exams = []
    
    for item in all_items:
        if any(kw in item.get("title", "").lower() for kw in keywords):
            date_str = item.get("start") or item.get("due", "")
            try:
                dt_obj = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                if dt_obj >= today:
                    future_exams.append({"item": item, "date": dt_obj})
            except:
                continue
    
    # Fallback 1: No exams, show Overdue Tasks counter
    if not future_exams:
        overdue_count = 0
        for t in data.get("reminders", []):
            due_str = t.get("due", "")
            if not due_str:
                continue
                
            try:
                due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
                if due_date < today:
                    overdue_count += 1
            except:
                continue

        # Fallback 2: No overdue tasks
        if overdue_count == 0:
            return create_icon_grid([
                (220, [567, 647, 727]),
                (302, [567, 647, 727])
            ])

        return [
            {"type": "image", "x": 567, "y": 212, "content": "module-overdue-tasks"},

            {"type": "text", "x": 640, "y": 260, "content": str(overdue_count), "font_size": "solway-normal-medium"}
        ]

    # Next Exam Module
    next_exam = min(future_exams, key=lambda x: x["date"])
    diff = (next_exam["date"] - today).days

    if diff == 0:
        val_num, val_txt = "today", "Good Luck!"
    else:
        val_num, val_txt = str(diff), "days"

    exam_title = truncate_with_ellipsis(next_exam["item"]["title"], 18)

    return [
        {"type": "image", "x": 567, "y": 212, "content": "module-next-exam"},

        {"type": "text", "x": 640, "y": 260, "content": f"{val_num}", "font_size": "solway-normal-medium"},
        {"type": "text", "x": 640, "y": 300, "content": f"{val_txt}", "font_size": "fredoka-normal-small"},
        {"type": "text", "x": 570, "y": 334, "content": exam_title, "font_size": "fredoka-normal-small"}
    ]

# Modules: Constellation
def module_constellation(constellation_points):
    # Fallback: Empty constellation
    if not constellation_points:
        return create_icon_grid([
            (400, [567, 647, 727])
        ])

    ORIGINAL_X, ORIGINAL_Y = 560, 396
    WIDTH = 220
    HEIGHT = 60

    center_x = ORIGINAL_X + 5 + (WIDTH / 2)
    center_y = ORIGINAL_Y + 5 + (HEIGHT / 2)
    
    max_rx = WIDTH / 2
    max_ry = HEIGHT / 2

    results = []
    prev_coords = None

    for p in constellation_points:
        angle_rad = p["angle"] * 2 * math.pi
        x_curr = center_x + (p["radius"] * max_rx * math.cos(angle_rad))
        y_curr = center_y + (p["radius"] * max_ry * math.sin(angle_rad))

        results.append({"type": "rectangle", "x": int(x_curr), "y": int(y_curr), "w": 3, "h": 3, "fill": 0})

    return results