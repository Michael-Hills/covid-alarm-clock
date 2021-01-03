import json
import requests

with open('config.json') as f:

    json_file = json.load(f)
news_api_key = json_file["keys"]["news-API-key"]

def test_access_news():

    news_url = "https://newsapi.org/v2/top-headlines?country=gb&apiKey=" + news_api_key
    news_response = requests.get(news_url)
    assert news_response.status_code == 200
