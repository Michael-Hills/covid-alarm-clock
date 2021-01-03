from main import weather_data_json

def test_status():
    assert type(weather_data_json()) == dict
