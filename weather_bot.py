# -*- coding: utf-8 -*-
import requests
import sqlite3
import json
import datetime
from config import bot, API


language = ''


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

    bot.send_message(message.chat.id, 'Привет, выберите язык для дальнейшего общения.\n\n'
                                      'Hi, choose a language for further communication\n\n'
                                      'Hallo, wählen Sie eine Sprache für die weitere Kommunikation\n\n'
                                      '/ru - Русский\n'
                                      '/en - English\n'
                                      '/de - Deutsch')


@bot.message_handler(commands=['ru'])
def start_message(message):
    global language
    language = 'ru'

    bot.send_message(message.chat.id, 'Привет, напишите мне любой город, и я покажу прогноз погоды для этого города.\n'
                                      'Введите /history, чтобы просмотреть историю последних пяти запросов.')


@bot.message_handler(commands=['en'])
def start_message(message):
    global language
    language = 'en'

    bot.send_message(message.chat.id, 'Hi, write the name of any city and I will show you the weather '
                                      'forecast for it.\n'
                                      'Type /history to view the history of the last five queries.')


@bot.message_handler(commands=['de'])
def start_message(message):
    global language
    language = 'de'

    bot.send_message(message.chat.id, 'Hallo, geben Sie den Namen einer beliebigen Stadt ein und ich zeige Ihnen '
                                      'die Wettervorhersage für diese Stadt.\n'
                                      'Schreiben Sie /history, um den Verlauf der letzten fünf Abfragen anzuzeigen.')


@bot.message_handler(commands=['history'])
def history(message):
    global language
    conn = sqlite3.connect('weather_data.sql')
    cur = conn.cursor()

    if language == 'ru':
        cur.execute(f'''SELECT city FROM weather
        WHERE UserId = {message.from_user.id} ORDER BY timestamp DESC LIMIT 5''')
        users = cur.fetchall()[::-1]
        info = 'Ваша история поиска:\n\n'
        for i in range(len(users)):
            info += f'{i+1}) {users[i][0]}\n'
    elif language == 'en':
        cur.execute(f'''SELECT city FROM weather
        WHERE UserId = {message.from_user.id} ORDER BY timestamp DESC LIMIT 5''')
        users = cur.fetchall()[::-1]
        info = 'Your search history:\n\n'
        for i in range(len(users)):
            info += f'{i+1}) {users[i][0]}\n'
    else:
        cur.execute(f'''SELECT city FROM weather
        WHERE UserId = {message.from_user.id} ORDER BY timestamp DESC LIMIT 5''')
        users = cur.fetchall()[::-1]
        info = 'Ihr Suchverlauf:\n\n'
        for i in range(len(users)):
            info += f'{i+1}) {users[i][0]}\n'

    cur.close()
    conn.close()
    bot.send_message(message.chat.id, info)


@bot.message_handler(content_types=['text'])
def get_weather(message):
    global language

    city_name = message.text.strip()
    city = city_name.lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    data = json.loads(res.text)
    try:
        if language == 'ru':
            bot.reply_to(message, f'В городе {city_name} сейчас {data["main"]["temp"]}°C')

            conn = sqlite3.connect('weather_data.sql')
            cur = conn.cursor()

            cur.execute("INSERT INTO weather (UserId, city, timestamp ) VALUES (?, ?, ?)",
                        (message.from_user.id, city_name, datetime.datetime.now()))
            conn.commit()
            cur.close()
            conn.close()
        elif language == 'en':
            bot.reply_to(message, f'It is currently {data["main"]["temp"]}°C in {city_name}')

            conn = sqlite3.connect('weather_data.sql')
            cur = conn.cursor()

            cur.execute("INSERT INTO weather (UserId, city, timestamp ) VALUES (?, ?, ?)",
                        (message.from_user.id, city_name, datetime.datetime.now()))
            conn.commit()
            cur.close()
            conn.close()
        else:
            bot.reply_to(message, f'In {city_name} beträgt die Temperatur derzeit {data["main"]["temp"]}°C.')

            conn = sqlite3.connect('weather_data.sql')
            cur = conn.cursor()

            cur.execute("INSERT INTO weather (UserId, city, timestamp ) VALUES (?, ?, ?)",
                        (message.from_user.id, city_name, datetime.datetime.now()))
            conn.commit()
            cur.close()
            conn.close()
    except KeyError:
        if language == 'ru':
            bot.reply_to(message, f'Вы ошиблись в названии города или его не существует.')
        elif language == 'en':
            bot.reply_to(message, f"You got the name of the city wrong or it doesn't exist.")
        else:
            bot.reply_to(message, f'Sie haben den Namen der Stadt falsch geschrieben oder sie existiert gar nicht.')


bot.infinity_polling()
