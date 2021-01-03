from main import get_weather_data

test_data = {'coord': {'lon': -3.53, 'lat': 50.72}, 'weather': [{'id': 804, 'main': 'Clouds',
'description': 'overcast clouds', 'icon': '04n'}], 'base': 'stations', 'main': {'temp': 282.85,
'feels_like': 282.22, 'temp_min': 282.04, 'temp_max': 283.15, 'pressure': 1024, 'humidity': 93},
'visibility': 10000, 'wind': {'speed': 0.45, 'deg': 236, 'gust': 1.34}, 'clouds': {'all': 100},
'dt': 1606757188, 'sys': {'type': 3, 'id': 2005600, 'country': 'GB', 'sunrise': 1606722796,
'sunset': 1606752778}, 'timezone': 0, 'id': 2649808, 'name': 'Exeter', 'cod': 200}

def test_weather_functionality():
    assert(get_weather_data(test_data)) == {'title': "Current Weather Data", 'content': "The current weather description " +
    "in Exeter is overcast clouds with a temperature of 8.85°, which feels like 8.85°, a max of 9.85° and a min of 8.85°"}
