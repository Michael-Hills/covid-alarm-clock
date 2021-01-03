"""This module contains the functionality of a smart Covid alarm clock, in which alarms
can be set with briefings decided by the user. It also adds notifications automatically.
Both notifications and alarms get data from API calls"""

import json
import re
from datetime import datetime
import sched
import logging
import time
from flask import request
from flask import Flask
from flask import render_template
from flask import Markup
import requests
import pyttsx3
from uk_covid19 import Cov19API

alarms = []
notifications = []
deleted_notifications = []
news_notif = []

s = sched.scheduler(time.time, time.sleep)

log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler = logging.FileHandler('log.txt')
handler.setFormatter(formatter)
logger = logging.getLogger('file_log')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

#open the config file and import the information needed
with open('config.json') as f:

    logger.info("Config file Opened")
    json_file = json.load(f)
news_api_key = json_file["keys"]["news-API-key"]
news_filters = json_file["filters"]["News Filters"]
news_filters = news_filters.split(",")
weather_api_key = json_file['keys']['weather-API-key']
location = json_file['filters']['location']
covid_filters = json_file['covid-api']['filters']
threshold = json_file['covid-api']['thresholds']

app = Flask(__name__)

#run this function every time page is refreshed
@app.route('/')
@app.route('/index')
def index():
    """This function runs every time the page is refreshed

    It runs all the other functions and adds data collected to the web page using flask"""

    get_notifications()
    current_weather = weather_data_json()
    get_weather_data(current_weather)
    covid_data = covid_data_json()
    get_covid_data(covid_data)


    #get all information when an alarm is created
    time = request.args.get("alarm")
    alarm_title = request.args.get("two")
    alarm_news = request.args.get("news")
    alarm_weather = request.args.get("weather")


    #see whether the alarm requires news and weather briefings
    if alarm_title and time:

        title_date = time.split("T")
        title = alarm_title + " at " + title_date[1] + " on " + title_date[0]

        if alarm_weather == 'weather':
            y_n_weather = "Yes"
        else:
            y_n_weather = "No"
        if alarm_news == 'news':
            y_n_news = "Yes"
        else:
            y_n_news = "No"

        content = "News: " + y_n_news + " Weather: " + y_n_weather
        alarm = {"time": time,"title": title ,"news":alarm_news,
        "weather":alarm_weather, "content": content}
        #add alarm to list of alarms and schedule it to speak
        if alarm not in alarms:
            if alarm['title'] not in [x['title'] for x in alarms]:
                if (valid_alarm(time))[0]:
                    alarms.append(alarm)
                    logger.info("Valid Alarm Created: " + alarm['title'])
                    delay = (valid_alarm(time))[1]
                    s.enter(delay,1,to_speak, argument = (alarm,))
                    logger.info("Alarm added to schedule")
            else:
                logger.warning("Invalid Alarm, Title already in alarms")


    #remove notification if close button is clicked
    cancel_notif = request.args.get("notif")
    for notification in notifications:
        if notification['title'] == cancel_notif:
            notifications.remove(notification)
            deleted_notifications.append(notification)
            if notification in news_notif:
                news_notif.remove(notification)


            logger.info("Notification " + notification['title'] + " removed")

    #remove alarm if close button is clicked
    cancel_alarm = request.args.get("alarm_item")
    for canc_alarm in alarms:
        if canc_alarm['title'] == cancel_alarm:
            alarms.remove(canc_alarm)
            logger.info("Alarm Cancelled: " + cancel_alarm)

    s.run(blocking=False)

    return render_template('index.html', notifications = notifications,
    title = "Covid Alarm Clock", alarms = alarms,image = 'covidclock.jpg')



def get_notifications():
    """this function gets the news headlines and adds them to the notifications

    the news is filtered using the filters from the config file
    it does not return anything, as the notifications are a global variable"""
    #create the fill URL from the base url and the api key from the config file
    news_url = "https://newsapi.org/v2/top-headlines?country=gb&apiKey=" + news_api_key
    news_response = requests.get(news_url)
    #if access to api is successful
    if news_response.status_code == 200:
        news = news_response.json()
        articles = news['articles']
        #filter through the news using config file filters
        for article in articles:
            for filter in news_filters:
                if (re.search(filter,str(article['title']), re.IGNORECASE)
                or re.search(filter,str(article['description']), re.IGNORECASE)):
                    url = str(article['url'])
                    html = Markup("<a href=\"" + url + "\">Click here for full article</a>")
                    headline = {'title':article['title'],'content':html}
                    if headline not in notifications:
                        if headline not in deleted_notifications:
                            news_notif.insert(0,headline)
                            notifications.insert(0,headline)

        logger.info("News notifications added")

    else:
        logger.error("Failed to access news api")


def valid_alarm(alarm) -> bool:
    """this function checks if the alarm is valid and calculates the delay

    an alarm is valid if it is set into the future, and the delay is calculated
    in seconds to the alarm time.
    Argument: alarm takes the time of the current alarm entered by the user in
    the form of a dictionary.
    It also returns 2 variables, the first being whether
    or not the alarm is valid and the second being the delay"""

    #strip the alarm of all the unneeded characters and format for use
    alarm = alarm.replace("T","-")
    alarm = datetime.strptime(alarm,"%Y-%m-%d-%H:%M")
    current_date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    current_date = datetime.strptime(current_date,"%Y-%m-%d-%H:%M:%S")
    difference = alarm - current_date
    delay = difference.total_seconds()
    #if delay is negative, alarm is invalid
    if delay <= 0:
        logger.warning("Invalid alarm entered. Alarm not added")
        return False, delay
    else:
        return True, delay

def to_speak(alarm):
    """This function adds the content to the tts module and runs it to to_speak

    it decides what content to speak depending on user input of which briefings.

    Argument: alarm is the current alarm added by the user"""

    #only announce alarm if it has not been deleted
    if alarm in alarms:

        speak = ""

        #check type as if error in collecting data, None will be returned
        covid_data = covid_data_json()
        corrona_data = get_covid_data(covid_data)
        if type(corrona_data) == dict:
            speak = speak + corrona_data['content']

        if alarm['weather'] == 'weather':
            current_weather = weather_data_json()
            weather_update = get_weather_data(current_weather)
            if type(weather_update) == dict:
                speak = speak + weather_update['content']


        if alarm['news'] == 'news':
            headlines = news_notif[:3]
            if len(headlines) > 0:
                speak = speak + "The headlines are: "
                for headline in headlines:
                    speak = speak + str(headline['title'])
            else:
                speak = (speak + "There are no headlines that fit the selected filters, or" +
                " they have all been seen and removed from notifications")
                logger.info("No headlines to announce")

        #runs the tts module to say speak variable and remove the alarm once its finished
        engine = pyttsx3.init()
        alarms.remove(alarm)
        engine.say(speak)
        engine.runAndWait()
        engine.stop()
        logger.info("Alarm Sounded")
    

def covid_data_json() -> dict:
    """This function retrieves covid data from the corronavirus api and creates a json file

    It selects the data from the location from the config file and returns returns a dictionary
    of the json file. The data is split into 2 JSON files, as the covid module only lets you
    filter latest by 1 stat, and deaths are not added until the next day"""

    covid_deaths_structure = {"date": "date","areaName": "areaName",
    "newDeathsByDeathDate": "newDeathsByDeathDate"}

    covid_cases_structure = {'date': 'date', "areaName": "areaName",
    "newCasesByPublishDate":"newCasesByPublishDate"}

    #get covid death data on last reported deaths
    covid_api_deaths = Cov19API(filters=covid_filters, structure=covid_deaths_structure,
    latest_by = "newDeathsByDeathDate")
    latest_covid_deaths = covid_api_deaths.get_json()

    #get covid cases data from last reported cases
    covid_api_cases = Cov19API(filters=covid_filters, structure=covid_cases_structure,
    latest_by = "newCasesByPublishDate")
    latest_covid_cases = covid_api_cases.get_json()

    #combine the 2 JSON files and create a dictionary of all the relevant informaation
    latest_covid_data = {'casesDate':latest_covid_cases['data'][0]['date'],
    'areaName':latest_covid_cases['data'][0]['areaName'],
    'newCases':latest_covid_cases['data'][0]['newCasesByPublishDate'],
    'deathsDate':latest_covid_deaths['data'][0]['date'],
    'newDeaths':latest_covid_deaths['data'][0]['newDeathsByDeathDate']}

    logger.info("Covid data collected")


    return latest_covid_data #only returned one as this is merely for testing status in pytest files

def get_covid_data(covid_data) -> dict:
    """This function extracts relevant data from dictionary returned in previous function


    Arguments: covid_data is a dictionary from the previous file
    it returns a dictionary containing the content for notifications and alarms"""

    #retrieve data drom dictionary in argument
    location = covid_data['areaName']
    case_date = covid_data['casesDate']
    new_cases = covid_data['newCases']
    death_date = covid_data['deathsDate']
    new_deaths = covid_data['newDeaths']

    category = (int(new_cases) // int(threshold) + 1)

    #create the content for notififcations and alarms
    latest_data = {'title':"Latest Covid-19 Data",
    'content':"The last reported daily cases in " + str(location) +" was " +
    str(new_cases) + ", reported on " + str(case_date) + ". The last reported deaths was "
    + str(new_deaths) + ", reported on " + str(death_date) + ". This puts " + str(location) +
     " in Threshold " + str(category)}

    #add to notifications if not already in it
    if latest_data not in notifications:
        if latest_data not in deleted_notifications:
            for notif in notifications:
                if notif['title'] == "Latest Covid-19 Data":
                    #if covid data changes, add to notification and remove old data
                    notifications.remove(notif)
            notifications.insert(0,latest_data)
    logger.info("Covid data filtered")

    return latest_data


def weather_data_json() -> dict:
    """This function retrieves the current weather information from the weather API

    It selects the weather information from the loaction from the API and adds it
    to the notifications, as well as returning it to be used in the tts for the alarms"""

    weather_url = ("https://api.openweathermap.org/data/2.5/weather?q=" +
    location +"&appid=" + weather_api_key)
    weather_response = requests.get(weather_url)
    if weather_response.status_code == 200:
        weather = weather_response.json()
        logger.info("Weather JSON created")
        return weather
    else:
        logger.error("Failed to access weather API")

def get_weather_data(weather) -> dict:
    """This function filters through the weather json file and returns relevant information

    Arguments: weather is a dictionary of the weather json file"""
    current_temp = str(kelvin_to_celcius(weather['main']['temp']))
    feels_temp = str(kelvin_to_celcius(weather['main']['feels_like']))
    max_temp = str(kelvin_to_celcius(weather['main']['temp_max']))
    min_temp = str(kelvin_to_celcius(weather['main']['temp_min']))
    current_weather_data = {'title': "Current Weather Data", 'content':
    "The current weather description in " +  weather['name'] + " is " +
    weather['weather'][0]['description'] + " with a temperature of " + current_temp +
     "°, which feels like " + feels_temp +"°, a max of " + max_temp +
      "° and a min of " + min_temp + "°"}

    if current_weather_data not in notifications:
        if current_weather_data not in deleted_notifications:
            for notif in notifications:
                if notif['title'] == "Current Weather Data":
                    #if weather changes, add to notification and remove old weather
                    notifications.remove(notif)
            notifications.insert(0,current_weather_data)

    logger.info("Weather data filtered")

    return current_weather_data


def kelvin_to_celcius(temp) -> float:
    """This function calculates the temperature in celcius from kelvin"""
    temp = int(temp)
    #calculate change and round to 2dp
    celcius = round((temp - 273.15),2)
    return celcius


if __name__ == '__main__':
    logger.info("Main code started running")
    app.run()
