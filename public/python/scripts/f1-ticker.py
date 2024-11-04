import time
import requests
import feedparser
import schedule
from RPLCD.i2c import CharLCD

# Initialize the LCD using RPLCD
lcd = CharLCD('PCF8574', 0x27)  # 0x27 is a common I2C address for LCDs

# LCD constants
LCD_WIDTH = 16  # Width of the LCD display

# Fetch race results from the Jolpica-F1 API
def fetch_race_data():
    url = "http://ergast.com/api/f1/current/last/results.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching race data")
            return None
    except Exception as e:
        print("Error:", e)
        return None

def get_race_results(data):
    results = []
    if data:
        race_name = data['MRData']['RaceTable']['Races'][0]['raceName']
        race_results = data['MRData']['RaceTable']['Races'][0]['Results']
        results.append(f"Race: {race_name}")
        for result in race_results:
            position = result['position']
            driver = result['Driver']['familyName']
            results.append(f"{position}: {driver}")
    return results

# Fetch championship standings (drivers)
def fetch_standings_data():
    url = "http://ergast.com/api/f1/current/driverStandings.json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching standings data")
            return None
    except Exception as e:
        print("Error:", e)
        return None

def get_standings(data):
    standings = []
    if data:
        driver_standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
        standings.append("Driver Standings")
        for standing in driver_standings:
            position = standing['position']
            driver = standing['Driver']['familyName']
            points = standing['points']
            standings.append(f"{position}: {driver} {points}pts")
    return standings

# Fetch news from GPBlog
def fetch_news():
    feed_url = "https://www.gpblog.com/en/rss"
    feed = feedparser.parse(feed_url)
    headlines = [entry.title for entry in feed.entries]
    return headlines

# Display all items (news, results, standings) in a unified feed
def display_feed():
    headlines = fetch_news()
    race_data = fetch_race_data()
    race_results = get_race_results(race_data)

    standings_data = fetch_standings_data()
    standings = get_standings(standings_data)

    # Combine all items into one feed
    feed_items = headlines + race_results + standings

    for item in feed_items:
        lcd.clear()
        if len(item) > LCD_WIDTH:
            for i in range(len(item) - LCD_WIDTH + 1):
                lcd.write_string(item[i:i + LCD_WIDTH])
                time.sleep(0.3)
                lcd.clear()
        else:
            lcd.write_string(item)
            time.sleep(2)

# Main loop
def job():
    lcd.clear()
    display_feed()

schedule.every(10).seconds.do(job)  # Run the job every 10 seconds

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
