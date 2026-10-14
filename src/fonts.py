from PIL import ImageFont

FONT_SOLWAY = "assets/fonts/Solway-Medium.ttf"
FONT_SOLWAY_BOLD = "assets/fonts/Solway-ExtraBold.ttf"
FONT_FREDOKA = "assets/fonts/Fredoka-Medium.ttf"
FONT_FREDOKA_BOLD = "assets/fonts/Fredoka-SemiBold.ttf"

FONTS = {
    "solway-normal-small": ImageFont.truetype(FONT_SOLWAY, 24),
    "solway-normal-medium": ImageFont.truetype(FONT_SOLWAY, 38),
    "solway-bold-small": ImageFont.truetype(FONT_SOLWAY_BOLD, 24),
    "solway-bold-medium": ImageFont.truetype(FONT_SOLWAY_BOLD, 38),
    "solway-bold-huge": ImageFont.truetype(FONT_SOLWAY_BOLD, 72),
    
    "fredoka-normal-small": ImageFont.truetype(FONT_FREDOKA, 24),
    "fredoka-bold-tiny": ImageFont.truetype(FONT_FREDOKA_BOLD, 18),
    "fredoka-bold-small": ImageFont.truetype(FONT_FREDOKA_BOLD, 24)
}