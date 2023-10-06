# -*- coding: utf-8 -*-
import telebot
import requests
import sqlite3
import json
from config import bot, API


@bot.message_handler(commands=['start'])
def start_message(message):
    conn = sqlite3.connect('weather_data.sql')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS weather(
        UserId INTEGER,
        city varchar(50))''')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Hi, enter me any city and I will display the weather forecast for that city.\n'
                                      'To see the history of requests type /history')


@bot.message_handler(commands=['history'])
def history(message):
    conn = sqlite3.connect('weather_data.sql')
    cur = conn.cursor()

    cur.execute(f'''SELECT city FROM weather
    WHERE UserId = {message.from_user.id}''')
    users = cur.fetchall()
    info = 'Your city search history:\n'
    for el in users:
        info += f'{el[0]}\n'

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, info)


@bot.message_handler(content_types=['text'])
def get_weather(message):
    city_name = message.text.strip()
    city = city_name.lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    data = json.loads(res.text)
    try:
        bot.reply_to(message, f'In {city_name}, it is currently {data["main"]["temp"]}°C')

        conn = sqlite3.connect('weather_data.sql')
        cur = conn.cursor()

        cur.execute("INSERT INTO weather (UserId, city) VALUES (?, ?)", (message.from_user.id, city_name))
        conn.commit()
        cur.close()
        conn.close()
    except KeyError:
        bot.reply_to(message, f'You made a mistake in the name of the city, or such a city does not exist')


bot.infinity_polling()

