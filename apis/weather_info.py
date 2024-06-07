import requests

def get_weather(city):
    api_key = "a9e5bb875d144939a8e230605240606"
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        location = data['location']
        current = data['current']

        location_info = f"Location: {location['name']}, {location['region']}, {location['country']}"
        local_time = f"Local Time: {location['localtime']}"
        temperature = f"Temperature: {current['temp_c']}°C / {current['temp_f']}°F"
        condition = f"Condition: {current['condition']['text']}"
        wind = f"Wind: {current['wind_mph']} mph / {current['wind_kph']} kph from {current['wind_dir']} ({current['wind_degree']}°)"
        humidity = f"Humidity: {current['humidity']}%"
        pressure = f"Pressure: {current['pressure_mb']} mb / {current['pressure_in']} in"
        visibility = f"Visibility: {current['vis_km']} km / {current['vis_miles']} miles"
        feels_like = f"Feels Like: {current['feelslike_c']}°C / {current['feelslike_f']}°F"
        uv_index = f"UV Index: {current['uv']}"

        weather_report = f"""
        {location_info}
        {local_time}
        {temperature}
        {condition}
        {wind}
        {humidity}
        {pressure}
        {visibility}
        {feels_like}
        {uv_index}
        """
    
        print(weather_report)
    else:
        return {"error": "City not found"}

if __name__ == "__main__":
    city = "New York"
    weather = get_weather(city)
    print("test completed")