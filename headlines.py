
import feedparser

from flask import Flask
from flask import render_template
from flask import request

from flask import make_response
import json
import datetime

import urllib
##
#server
import urllib2
#local
# import urllib.request
# import urllib.parse
##

app = Flask(__name__)


RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
			 'cnn': 'http://rss.cnn.com/rss/edition.rss',
			 'fox': 'http://feeds.foxnews.com/foxnews/latest',
			 'iol': 'http://www.iol.co.za/cmlink/1.640'}

#METRIC UNITS
#WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=8218c490e1db3cf7355a8fe1d6b41a4b"
#IMPERIAL (US) UNITS
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&APPID=8218c490e1db3cf7355a8fe1d6b41a4b"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=cefbae52dfae4e709f65288bcb711dee"

DEFAULTS = {'publication': 'bbc',
            'city': 'London,UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'
            }

def get_value_with_fallback(key):
	if request.args.get(key):
		return request.args.get(key)
	if request.cookies.get(key):
		return request.cookies.get(key)
	return DEFAULTS[key]

@app.route("/")
def home():
	# get customised headlines, based on user input or default
	publication = get_value_with_fallback("publication")
	articles = get_news(publication)
	
	# get customised weather based on user input or default
	city = get_value_with_fallback("city")
	weather = get_weather (city)
	
	# get customised currency based on user input or default
	currency_from = get_value_with_fallback("currency_from")
	currency_to = get_value_with_fallback("currency_to")
	rate, currencies = get_rate(currency_from, currency_to)
	
	# save cookies and return template
	response = make_response(render_template("home.html",
				articles=articles, weather=weather, 
				currency_from=currency_from,
				currency_to=currency_to, rate=rate,
				currencies=sorted(currencies)))
	expires = datetime.datetime.now() + datetime.timedelta(days=365)
	response.set_cookie("publication", publication, expires=expires)
	response.set_cookie("city", city, expires=expires)
	response.set_cookie("currency_from",
			currency_from, expires=expires)
	response.set_cookie("currency_to",
			currency_to, expires=expires)
	return response

def get_rate(frm, to):
	##
	# server 
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    # local -- machine
    # all_currency = urllib.request.urlopen(CURRENCY_URL).read()
    ##
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())


def get_news(publication):
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    ##
    # server
    query = urllib.quote(query)
    # local -- machine
    # query = urllib.parse.quote(query)
    ##
    url = WEATHER_URL.format(query)

	##
    # server
    data = urllib2.urlopen(url).read()
    # local -- machine
    # data = urllib.request.urlopen(url).read()
    ##
        
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name'],
                   'country': parsed['sys']['country']
                   }
    return weather

if __name__ == "__main__":
    app.run(port=5000, debug=True)

