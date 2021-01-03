from main import covid_data_json

def test_covid_status():
    assert (type(covid_data_json())) == dict #only returns dictionary if API is working
