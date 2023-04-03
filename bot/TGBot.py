import telebot
import json, os
from telebot import types
import ParserHTML


bot = telebot.TeleBot(os.environ.get('TRANSPORT_TGBOT_TOKEN'))


def markup_Reply_transport_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    bus_button = types.KeyboardButton("Автобус")
    tramway_button = types.KeyboardButton("Трамвай")
    trolleybus_button = types.KeyboardButton("Троллейбус")
    button_back = types.KeyboardButton("В начало")
    markup.add(button_back)
    markup.row(bus_button, trolleybus_button, tramway_button)
    return markup

def markup_Reply_num_transport_button(type_transport):
    with open(f"data/{type_transport}.json") as file:
        data = json.load(file)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_back = types.KeyboardButton("Назад")
    markup.add(button_back)
    button_list = []
    for i in data['response']:
        button = types.KeyboardButton(i)
        button_list.append(button)
    markup.row(*button_list)
    return markup

def text_data_transport_position(dict):
    if(len(dict)>0):
        output_str = []
        output_str.append(f'🔜Транспорт {dict[0]["EndStops"]}')
        for item in dict:
            if(item['Orient'] == 'forward'):
                if(item["Park"] == True):
                    if(item["Position"] == 'Between_Stops'):
                        str_data = f'❌Перед ост. {item["Stops"]}. ❗В парк {item["EndStops"]}'
                    if (item["Position"] == "Stops"): str_data = f'❌Ост. {item["Stops"]}. ❗В парк {item["EndStops"]}'
                    output_str.append(str_data)
                else:
                    if (item["Position"] == 'Between_Stops'):
                        str_data = f'⬇️Перед ост. {item["Stops"]}'
                    if (item["Position"] == "Stops"): str_data = f'⬇Ост. {item["Stops"]}.'
                    output_str.append(str_data)
        output_str.append('\n')
        output_str.append(f'🔙Транспорт {dict[len(dict)-1]["EndStops"]}')
        for item in dict:
            if(item['Orient'] == 'back'):
                if (item["Park"] == True):
                    if (item["Position"] == 'Between_Stops'):
                        str_data = f'❌Перед ост. {item["Stops"]}. ❗В парк {item["EndStops"]}'
                    if (item["Position"] == "Stops"): str_data = f'❌Ост. {item["Stops"]}. ❗В парк {item["EndStops"]}'
                    output_str.append(str_data)
                else:
                    if (item["Position"] == 'Between_Stops'):
                        str_data = f'⬇️Перед ост. {item["Stops"]}'
                    if (item["Position"] == "Stops"): str_data = f'⬇Ост. {item["Stops"]}.'
                    output_str.append(str_data)
        output_str = ' \n'.join(output_str)
        return output_str
    else:
        return 'На данный момент этот вид транспорта недоступен.'

#стартовая команда, создает одну кнопку для активации основного кода
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    route = types.KeyboardButton("Тип транспорта")
    markup.add(route)
    bot.send_message(message.chat.id,"Начало работы с ботом",reply_markup=markup)

#Исходя из json файла выводит вид доступного транспорта и создает для них кнопки
@bot.message_handler(content_types=['text'])
def choiсe_transport_type(message):
    message_b = ''
    with open('all_categories_dict.json', 'r') as file:#выводит доступные кнопки авт трол трам
        data = json.load(file)
    str_output = ', \n'.join(data.keys())

    mess_text = message.text
    if(mess_text == 'Тип транспорта'):
        markup = markup_Reply_transport_button()
        bot.send_message(message.chat.id,f"Вид транспорта:\n{str_output}",reply_markup=markup)

    if(mess_text in"Автобус" or mess_text in "Троллейбус" or mess_text in "Трамвай"):
        for i in str_output.split(","):
            i = i.replace('\n', '').strip()
            if i.lower() == mess_text.lower():#Проверяю соответствие сообщения списку доступного транспорта
                str=f'data/{i}.json'
                with open(str, "r") as file:
                    data = json.load(file)
                str_output_number = ', '.join(data['response'].keys())
                markup = markup_Reply_num_transport_button(i)
                bot.send_message(message.chat.id,f"Все номера({mess_text}):\n{str_output_number}\nВыберите необходимый\nНеобходимо подождать несколько секунд",reply_markup=markup)
                with open('background_message.json',"w") as file:
                    json.dump(message.json,file,indent=4,ensure_ascii=False)
                break

    if(message.text.isdigit()):
        with open('background_message.json', "r") as file:
            data = json.load(file)
        if (data['text'] in"Автобус" or data['text'] in "Троллейбус" or data['text'] in "Трамвай"):
            ParserHTML.position(message.text, data['text'])
            with open("position.json","r") as file:
                dict = json.load(file)
            text = text_data_transport_position(dict)
            markup = markup_Reply_transport_button()
            bot.send_message(message.chat.id, f"Список доступного транспорта:\n {text}", reply_markup=markup)
        else:
            markup = markup_Reply_transport_button()
            bot.send_message(message.chat.id, f"Введите необходимый вид транспорта:\n{str_output}",reply_markup=markup)
    if(mess_text == 'Назад'):
        markup = markup_Reply_transport_button()
        bot.send_message(message.chat.id, "Вы вернулись назад", reply_markup=markup)
    if (mess_text == 'В начало'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        route = types.KeyboardButton("Тип транспорта")
        markup.add(route)
        bot.send_message(message.chat.id, "Вы вернулись в начало", reply_markup=markup)


try:#Должно исключать падение бота во время перезагрузки сервера
    bot.polling(none_stop=True)
except Exception as e:
    print(e)

