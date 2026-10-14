import math
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from waveshare_epd import epd7in5_V2
from src.helpers import *
from src.fonts import FONTS
from src.unhinged_sentences import get_day_vibe, get_fact

# Fatal error screen
def refresh_display_fatal_error():
    epd = epd7in5_V2.EPD()
    epd.init()

    image = Image.open(f"assets/dashboard-error.bmp")
    draw = ImageDraw.Draw(image)
    
    display_elements = (
        create_icon_grid([
            (20, [22, 135, 248]),
            (80, [22, 135, 248]),
            (140, [22, 135, 248]),
            (200, [22, 135, 248]),
            (260, [22, 135, 248]),
            (320, [22, 135, 248]),
            (380, [22, 135, 248])
        ]))
    render_items(display_elements, draw, image)

    epd.display(epd.getbuffer(image))
    epd.sleep()

# Welcome screen
def refresh_display_welcome():
    epd = epd7in5_V2.EPD()
    epd.init()

    image = Image.open(f"assets/dashboard-welcome.bmp")
    draw = ImageDraw.Draw(image)
    
    display_elements = (
            create_icon_grid([
                (20, [22, 135, 248]),
                (80, [22, 135, 248]),
                (140, [22, 135, 248]),
                (200, [22, 135, 248]),
                (260, [22, 135, 248]),
                (320, [22, 135, 248]),
                (380, [22, 135, 248])
            ]))
    render_items(display_elements, draw, image)

    epd.display(epd.getbuffer(image))
    epd.sleep()