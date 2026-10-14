import os, random, requests, socket, json
from PIL import Image
from src.fonts import FONTS
from datetime import datetime

DAY_CONFIG_FILE = "data/day_config.json"

# Render the given items: Text, Images, Rectangles, and Lines
def render_items(elements, draw, image):
    for item in elements:
        if item["type"] == "text":
            font = FONTS.get(item.get("font_size", "fredoka-normal-small"))
            draw.text((item["x"], item["y"]), item["content"], font=font, fill=0)

        elif item["type"] == "image":
            image_path = os.path.join("assets", item["content"] + ".bmp")
            if os.path.exists(image_path):
                img_path = Image.open(image_path)
                image.paste(img_path, (item["x"], item["y"]))
        
        elif item["type"] == "rectangle":
            x, y, w, h = item["x"], item["y"], item["w"], item["h"]
            draw.rectangle([x, y, x + w, y + h], fill=item.get("fill", 0))
        
        elif item["type"] == "line":
            draw.line([(item["x1"], item["y1"]), (item["x2"], item["y2"])], fill=0, width=item.get("width", 1))

# Render status icons
def render_statuses(last_retrieved, image):
    x_pos = 15
    # Status: Data not refreshed
    if last_retrieved != datetime.now().strftime("%Y-%m-%d"):
        icon = Image.open("assets/status-sync.bmp")
        image.paste(icon, (x_pos, 445))
        x_pos += 25

    # Status: No wifi
    online = False
    try:
        socket.setdefaulttimeout(3)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("1.1.1.1", 53))
        online = True
    except (socket.timeout, OSError):
        online = False

    if not online:
        icon = Image.open("assets/status-wifi.bmp")
        image.paste(icon, (x_pos, 445))
        x_pos += 25

    # Statuses: Error retrieving...
    with open(DAY_CONFIG_FILE, 'r') as f:
        config = json.load(f)

        # Status: Error retrieving tasks/events data
        error_retrieval = config.get("error_retrieval")
        if error_retrieval:
            icon = Image.open("assets/status-error-data.bmp")
            image.paste(icon, (x_pos, 445))
            x_pos += 25

        # Status: Error retrieving lyrics data
        error_retrieval_lyrics = config.get("error_retrieval_lyrics")
        if error_retrieval_lyrics:
            icon = Image.open("assets/status-error-lyrics.bmp")
            image.paste(icon, (x_pos, 445))
            x_pos += 25

# Format due date into human-readable string (today, tomorrow, in x days, x days ago)
def format_due_date(due_string):
    if not due_string:
        return ":("
        
    now = datetime.now()
    
    try:
        due_date = datetime.strptime(due_string, "%Y-%m-%d").date()
        difference_date = (due_date - now.date()).days

        if difference_date == 0:
            return "today"
        elif difference_date == 1:
            return "tomorrow"
        elif difference_date == -1:
            return "yesterday"
        elif 1 < difference_date <= 7:
            return f"in {difference_date} days"
        elif -7 <= difference_date < -1:
            return f"{abs(difference_date)} days ago"
        else:
            return due_date.strftime("%b %d").lower()            
    except ValueError:
        return due_string

# Parse time into Python datetime
def parse_event_time(date_str):
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.replace(tzinfo=None) 
        except:
            return None

# Split title into 2 lines
def split_title(string, max_chars):
    if not string:
        return [":("]
    
    if len(string) <= max_chars:
        return [string]
    
    split_point = string.rfind(" ", 0, max_chars)
    
    if split_point == -1:
        split_point = max_chars

    first = string[:split_point].rstrip()
    second = string[split_point:].lstrip()
    
    if len(second) <= max_chars:
        return [first, second]
    
    return [first, second[:max_chars-3].rstrip() + "..."]

# Split title into multiple (infinite) lines
def split_title_multi(string, max_chars):
    if not string:
        return [":("]
    
    if len(string) <= max_chars:
        return [string]
    
    words = string.split()
    lines = []
    
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + (1 if current_line else 0) <= max_chars:
            current_line += (" " if current_line else "") + word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines if lines else [":("]

# Cut string with ellipsis
def truncate_with_ellipsis(string, max_chars):
    if not string:
        return ":("
    
    if len(string) <= max_chars:
        return string
        
    return string[:max_chars-3].rstrip() + "..."

# Create icon grid
def create_icon_grid(row_coords):
  return [
      {"type": "image", "x": x, "y": y, "content": f"icon-pattern/{random.randint(1, 32)}"}
      for y, x_list in row_coords
      for x in x_list
  ]

# Shuffle constellation's start point
def shuffle_constellation(points):
    if not points or len(points) < 2:
        return points
    
    start_index = random.randint(0, len(points) - 1)
    return points[start_index:] + points[:start_index]

# Reverse geocode coordinates
def reverse_geocode(coords, api_key):
    if not coords:
        return ":("
    
    coords_lat = coords[0]
    coords_lon = coords[1]

    url = f"https://api.tomtom.com/maps/orbis/places/reverseGeocode?position={coords_lon},{coords_lat}"
    headers = {"TomTom-Api-Key": api_key, "TomTom-Api-Version": "2", "Attributes": "results.address"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data_received = response.json()
        
        place_name = data_received["results"][0]["address"]["municipality"]
        
        return place_name
    except Exception:
        return ":("