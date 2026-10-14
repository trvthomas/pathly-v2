import json, random
from datetime import timedelta

# Lyrics
LYRICS_FILE = 'data/lyrics.json'
def get_lyrics():
    try:
        with open(LYRICS_FILE, 'r') as f:
            lyrics = json.load(f)
        
        item = random.choice(lyrics)
        
        return item['lyric'], item['song'], item['artist']
    except Exception:
        return "You promised me data, you promised me truth, Now all that is left is an empty parse roof", "Broken JSON", "The Missing Bytes"

array_day_vibe = [
    "Nothing for today!",
    "Free today?",
    "Nothing to worry about.",
    "Zero obligations.",
    "Blank calendar, yei!",
    "Officially unscheduled!",
    "No tasks, no stress."
]

# Day Vibe
def get_day_vibe():
    return random.choice(array_day_vibe)

# Fact
def get_fact(now):
    # Month progress
    progress_month_name = now.strftime("%B")
    day_of_month = now.day
    next_month = now.replace(day=28) + timedelta(days=4)
    last_day_of_month = (next_month - timedelta(days=next_month.day)).day
    progress_month = int((day_of_month / last_day_of_month) * 100)

    # Year Progress
    day_of_year = int(now.strftime("%j"))
    progress_year = int((day_of_year / 365) * 100)

    # Month Calculations
    days_left_month = last_day_of_month - day_of_month
    hours_left_month = days_left_month * 24
    sleep_hours_month = days_left_month * 8
    sleep_naps_month = round(sleep_hours_month / 1.5)

    # Year Calculations
    days_left_year = 365 - day_of_year
    hours_left_year = days_left_year * 24
    sleep_hours_year = days_left_year * 8
    sleep_naps_year = round(sleep_hours_year / 1.5)
    movies = [
        ("Backrooms", 1.75),
        ("Big Hero 6", 1.70),
        ("Everything Everywhere All at Once", 2.32),
    ]
    movie_title, movie_hours = random.choice(movies)
    movie_rewatches = round(days_left_year * 24 / movie_hours, 1)

    # CA Seasons
    month = now.month
    day = now.day
    if (month == 12 and day >= 21) or month <= 2 or (month == 3 and day < 20):
        season = "winter"
    elif (month == 3 and day >= 20) or month <= 5 or (month == 6 and day < 21):
        season = "spring"
    elif (month == 6 and day >= 21) or month <= 8 or (month == 9 and day < 22):
        season = "summer"
    else:
        season = "fall"

    # Beginning of Month
    month_early = [
        f"{progress_month_name} just started and you're already on vacation. Chill.",
        f"{days_left_month} days left in {progress_month_name}. That's {hours_left_month} hours. Use then wisely.",
        f"Only {progress_month}% into {progress_month_name}. Plenty of time to do... up to you.",
        f"{sleep_hours_month} hours of sleep available this month. Use them."
    ]
    # Mid Month
    month_mid = [
        f"Halfway through {progress_month_name}. {days_left_month} days left and {sleep_hours_month} sleep hours available.",
        f"{progress_month}% into {progress_month_name}. Coasting.",
        f"{days_left_month} days left in {progress_month_name}. That's {sleep_naps_month} naps. Just saying.",
        f"{hours_left_month} hours left in {progress_month_name}. You won't remember most of them."
    ]
    # End Month
    month_late = [
        f"{progress_month_name} is {progress_month}% gone. {days_left_month} days left. Make them weird.",
        f"Only {days_left_month} days until {progress_month_name} is a memory.",
        f"{hours_left_month} hours left in {progress_month_name}. That's {sleep_naps_month} naps if you're efficient.",
        f"{progress_month_name} is almost over and you have zero tasks. Legendary."
    ]
    # Year: Winter
    year_winter = [
        f"The year is {progress_year}% done and it's still cold. {days_left_year} days to fix that.",
        f"Only {progress_year}% through the year. You could rewatch {movie_title} {movie_rewatches}x before December.",
        f"{hours_left_year} hours of year remaining, {sleep_hours_year} of them could be sleep. Tempting."
    ]
    # Year: Spring
    year_spring = [
        f"{days_left_year} days left in the year. Plenty of time to go outside and get some sun.",
        f"{progress_year}% through the year and the weather finally cooperated.",
        f"{days_left_year} days left. That's {movie_rewatches} {movie_title} rewatches. Priorities."
    ]
    # Year: Summer
    year_summer = [
        f"It's summertime! {hours_left_year} hours left in the year. {sleep_hours_year} of them could be sleep.",
        f"{progress_year}% through the year. Peak vacation energy.",
        f"{days_left_year} days until January. You could have {sleep_naps_year} naps between now and then.",
        f"The year is {progress_year}% done and it's too hot to care about the rest.",
    ]
    # Year: Fall
    year_fall = [
        f"Fall already. {days_left_year} days left. The year is closing in.",
        f"{progress_year}% through the year. {days_left_year} days to make it count.",
        f"Only {days_left_year} days left in the year. That's {movie_rewatches} {movie_title} rewatches. Respect the time."
    ]

    # Pick category
    if progress_month < 30:
        month_fact = random.choice(month_early)
    elif progress_month < 70:
        month_fact = random.choice(month_mid)
    else:
        month_fact = random.choice(month_late)

    year_facts = {
        "winter": year_winter,
        "spring": year_spring,
        "summer": year_summer,
        "fall": year_fall,
    }
    year_fact = random.choice(year_facts[season])

    array_fact = [month_fact, year_fact]

    return random.choice(array_fact)