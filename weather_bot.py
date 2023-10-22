# -*- coding: utf-8 -*-
import requests
import sqlite3
import json
import datetime
from config import bot, API


@bot.message_handler(commands=['start'])
def start_message(message):
    conn = sqlite3.connect('weather_data.sql')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS weather(
        UserId INTEGER,
        city varchar(50),
        timestamp TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Привет, напиши мне любой город и я выведу прогноз погоды в нем.\n'
                                      'Введите /history для того, чтобы посмотреть историю последних пяти запросов')


@bot.message_handler(commands=['history'])
def history(message):
    conn = sqlite3.connect('weather_data.sql')
    cur = conn.cursor()

    cur.execute(f'''SELECT city FROM weather
    WHERE UserId = {message.from_user.id} ORDER BY timestamp DESC LIMIT 5''')
    users = cur.fetchall()[::-1]
    info = 'Ваша история поиска городов:\n\n'
    for i in range(len(users)):
        info += f'{i+1}) {users[i][0]}\n'

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
        bot.reply_to(message, f'В городе {city_name} сейчас {data["main"]["temp"]}°C')

        conn = sqlite3.connect('weather_data.sql')
        cur = conn.cursor()

        cur.execute("INSERT INTO weather (UserId, city, timestamp ) VALUES (?, ?, ?)",
                    (message.from_user.id, city_name, datetime.datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
    except KeyError:
        bot.reply_to(message, f'Вы допустили ошибку в названии города, либо такого горда не существует')


bot.infinity_polling()
