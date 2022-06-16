import telebot
import config
from telebot import types
from requests import get

# Ф-я для проверки id пользователя на возможность взаимодействия с ботом.
def is_allowed_user(message):
    user_id = message.from_user.id
    if user_id not in config.allowed_ids:
        txt = "Я незнакомым людям не отвечаю."
        bot.send_message(message.chat.id, text=txt)
        return False
    
    return True


#ф-я для работые с погодой через API яндекса
def get_weather(lon, lat, yandexkey):

    # статусы облачности
    condition_dict = {
        'clear':'Ясно.',
        'partly-cloudy':'Малооблачно.',
        'cloudy':'Облачно с прояснениями.',
        'overcast':'Пасмурно.',
        'drizzle':'Морось.',
        'light-rain':'Небольшой дождь.',
        'rain':'Дождь.',
        'moderate-rain':'Умеренно сильный дождь.',
        'heavy-rain':'Сильный дождь.',
        'continuous-heavy-rain':'Длительный сильный дождь.',
        'showers':'Ливень.',
        'wet-snow':'Дождь со снегом.',
        'light-snow':'Небольшой снег.',
        'snow':'Снег.',
        'snow-showers':'Снегопад.',
        'hail':'Град.',
        'thunderstorm':'Гроза.',
        'thunderstorm-with-rain':'Дождь с грозой.',
        'thunderstorm-with-hail':'Гроза с градом.',
    }

    # статусы осадков
    prec_type_dict = {
        0:"Без осадков.",
        1:"Дождь.",
        2:"Дождь со снегом.",
        3:"Снег.",
    }

    # статусы ветра
    wind_dir_dict = {
        'nw':'Северо-западный.',
        'n':'Северный.',
        'ne':'Северо-восточный.',
        'e':'Восточный.',
        'se':'Юго-восточный.',
        's':'Южный.',
        'sw':'Юго-западный.',
        'w':'Западный.',
        'с':'Штиль.',
    }



    url = 'https://api.weather.yandex.ru/v2/forecast'
    header = {'X-Yandex-API-Key': yandexkey}
    param ={
            'lon':lon,
            'lat':lat,
            'lang':'ru_RU',
            'limit':0,
            'hours':'false',
            'extra':'false',
    }


    response = get(url=url, headers=header, data=param)
    json_response = response.json()['fact']

    resp_temp = json_response['temp']
    resp_condition = json_response['condition']
    resp_feels_like = json_response['feels_like']
    reps_prec_type = json_response['prec_type']
    resp_wind_speed = json_response['wind_speed']
    resp_wind_dir = json_response['wind_dir']


    condition_out = f"Осадки: {condition_dict[resp_condition]} {prec_type_dict[reps_prec_type]}"
    temp_out = f"Температура: {resp_temp}°C. Ощущается как {resp_feels_like}°C"
    wind_out = f"Ветер: {wind_dir_dict[resp_wind_dir]} {resp_wind_speed} м/с"
    weather=f"{temp_out}\n{condition_out}\n{wind_out}"

    return weather



bot = telebot.TeleBot(config.bot_token)


@bot.message_handler(commands=['start'])
def start(message):
    if is_allowed_user(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton("Узнать погоду", request_location=True)
        markup.add(btn)
        bot.send_message(message.chat.id, text="Нажми на кнопку, запрошу погоду по текущим координатам.", reply_markup=markup)



@bot.message_handler(content_types=['location'])
def get_location(message):
    # Отвечать только разрешенным пользователям
    if is_allowed_user(message):
        if message.location is not None:
            longitude = message.location.longitude
            latitude = message.location.latitude
            # получение погоды от яндекса по заданным координатам
            txt = get_weather(longitude, latitude, config.yandex_api_key)
        else:
            txt = "Не удалось получить Ваши координаты"
        
        bot.send_message(message.chat.id, text=txt)


if __name__ == "__main__":
    bot.polling(none_stop=True)
