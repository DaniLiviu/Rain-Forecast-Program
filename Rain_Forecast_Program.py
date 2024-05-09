import requests
import datetime
import json
import geocoder

API_URL = "https://api.open-meteo.com/v1/forecast"
weather_cache = {}
weather_cache_file = 'weather_data.txt'

# Load cached data from the file if it exists
try:
    with open(weather_cache_file, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            date = list(data.keys())[0]
            weather_cache[date] = data[date]
except FileNotFoundError:
    pass

def get_lat_lon(city_name=None):
    if city_name:
        # Get latitude and longitude based on city name using geocoder
        g = geocoder.osm(city_name)
        if g.ok:
            return g.latlng
    # Default to a predefined location (e.g., London)
    return [51.5074, -0.1278]

while True:
    searched_date = input("Enter date (YYYY-mm-dd) or leave blank for tomorrow: ")
    
    if not searched_date:
        searched_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        try:
            datetime.datetime.strptime(searched_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please enter the date in YYYY-mm-dd format.")
            continue
    
    #Get location data from user
    city_name = input("Enter city name or leave blank for default location: ")
    lat_lon = get_lat_lon(city_name)

    #Check Cached Data
    if searched_date in weather_cache:
        weather_data = weather_cache[searched_date]
        print("Using cached data...")
    else:
        # Make API Request
        latitude, longitude = lat_lon
        url = f"{API_URL}?latitude={latitude}&longitude={longitude}&daily=precipitation_sum&timezone=Europe%2FLondon&start_date={searched_date}&end_date={searched_date}"
        
        response = requests.get(url)
        
        # Handle API Response
        if response.status_code == 200:
            weather_data = response.json()
            # Optionally, store in the cache
            weather_cache[searched_date] = weather_data
        else:
            print("API request failed.")
            continue

    # Extract and Print Precipitation Information
    try:
        daily_data = weather_data['daily']
        precipitation_sum = daily_data['precipitation_sum'][0]

        if precipitation_sum > 0.0:
            print(f"It will rain. Precipitation value: {precipitation_sum} mm")
        elif precipitation_sum == 0.0:
            print("It will not rain.")
        else:
            print("I don't know! (No data or negative value)")
    except KeyError:
        print("Unexpected data format.")

    # Save Data to File 
    with open(weather_cache_file, 'a') as f:
        f.write(json.dumps({searched_date: weather_data}) + '\n')

    #  User Continuation
    continuation = input("Do you want to check another date (yes/no)? ").strip().lower()
    if continuation != 'yes':
        break
