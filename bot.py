# Добавить настройку строгости отбора новостей
# Добавить инфографику профиля на основе отмеченный новостей
# Записывать ошибки/логи в файл
# Добавить кнопки для возврата новостей
# добавить возомжность отключить "скрытые" новости. Можно в меню добавить кнопку «показать убранное за последний день»
# можно ли отслеживать клик по ссылке на новость
# Написать валидацию json и текста
# добавить выбор тематики, если я добавлю теги и ключевые слова
# может быть можно справшивать ключевые слова? или отмечать какие подходят
# есть более крупная бибилиотека по новостям https://spacy.io/models/ru от natasha
# бот отправляет одинаковые новости (послушный ребенок)

from ddl import read_all_users, add_to_schedule, create_sources, read_sources, remove_sources, add_sources
from reader_saver import save_user_data, load_last_news, save_last_ten_declined_news, load_last_ten_declined_news
from prep_embeddings import get_message_rule, create_user_embeddings, find_intersections

from telebot import types
from telegram_bot_api_key import token

import telebot
import json
import time
import shutil

from threading import Thread

from load_last_news_schedule import start_schedule

bot = telebot.TeleBot(token)

# Загружаем список источников для обновления 
with open(f'./sources.json', 'r') as f:
    file = json.load(f)
    sources = file['list']
    sources_russian = file['list_russian']
    mapping = file["mapping"]

def keyboard(user_id):

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    user_sources = read_sources(user_id)

    for source in user_sources:
        keyboard.add(types.KeyboardButton(mapping[source]))
    for source in sources:
        if source not in user_sources:
            keyboard.add(types.KeyboardButton('Вернуть ' + mapping[source]))

    keyboard.add(types.KeyboardButton('Скрыть'))

    return keyboard

@bot.message_handler(commands=["show_declined"])
def show_declined(message):
    
    user_id = message.chat.id

    data = load_last_ten_declined_news(message.chat.id)
    for news in data:

        news_key = list(news.keys())[0]

        markup_inline = types.InlineKeyboardMarkup()

        item_yes = types.InlineKeyboardButton(text = 'Отметить как интересное', callback_data = str(user_id) + '_1_' + news_key)

        markup_inline.add(item_yes)

        bot.send_message(text = news[news_key]['news_title'] + '\n' + news[news_key]['news_link'], chat_id = user_id, reply_markup = markup_inline)
        
        time.sleep(.1)

    bot.send_message(text = 'Все последние 10 новостей показаны', chat_id = user_id)

@bot.message_handler(commands=["start"])
def new_user_action(message):

    user_id = message.chat.id

    add_to_schedule([user_id])
    create_sources(user_id)
    bot.send_message(user_id, "Привет! Я бот, который помогает тебе читать новости.")

@bot.message_handler(commands=["delete_history"])
def delete(message):

    user_id = message.chat.id

    shutil.rmtree(rf".\data\users\{user_id}")
    bot.send_message(user_id, "Вся память стерта, все теперь заново")

@bot.message_handler(commands=["change_sources"])
def change_sources(message):
    
    user_id = message.chat.id

    bot.send_message(user_id, text="Какие источники скрыть/вернуть?", reply_markup = keyboard(user_id))


@bot.message_handler(content_types=['text'])
def show_declined(message):

    user_id = message.chat.id
    sr_eng = ''

    for source in mapping:
        if message.text == mapping[source]:
            sr_eng = source
    if sr_eng != '':

        remove_sources(user_id, sr_eng)
        
        bot.send_message(user_id, f'Источник "{message.text}" убран из выдачи', reply_markup = keyboard(user_id))

    if 'Вернуть' in message.text:
        source = message.text.split()[1]
        for source_eng in mapping:
            if source == mapping[source_eng]:
                sr_eng = source_eng
                break
        add_sources(user_id, sr_eng)
        bot.send_message(user_id, f'Источник "{source}" возвращен в выдачу', reply_markup = keyboard(user_id))

    if 'Скрыть' == message.text:
        bot.send_message(user_id, "Ок!", reply_markup=types.ReplyKeyboardRemove())

@bot.callback_query_handler(func = lambda call: True)
def query_handler(call):
    
    call_data = call.data.split('_')
    save_user_data(call_data)

    if '_1_' in call.data:
        bot.answer_callback_query(callback_query_id=call.id, text="Ок, будет больше таких новостей", cache_time = 3)
    elif '_0_' in call.data:
        bot.answer_callback_query(callback_query_id=call.id, text="Ок, будет меньше таких новостей", cache_time = 3)
        bot.delete_message(chat_id = call.message.chat.id, message_id = call.message.message_id)

    create_user_embeddings(call_data[0])

    bot.answer_callback_query(call.id)

def send_last_news():

        for source in sources:

            load = load_last_news(source)

            if load[0] == 1:
                news_hash, news_link, news_title, _ = load[1]

                for user in read_all_users():

                    print(user)
                    user_sources = read_sources(user)

                    if source in user_sources:

                        markup_inline = types.InlineKeyboardMarkup()

                        item_yes = types.InlineKeyboardButton(text = 'Огонь', callback_data = str(user) + '_1_' + news_hash)
                        item_no = types.InlineKeyboardButton(text = 'Не интересно', callback_data = str(user) + '_0_' + news_hash)

                        markup_inline.add(item_yes, item_no)

                        gmr, news_title_emb = get_message_rule(news_title, user)

                        print(gmr, news_title)

                        if gmr == 1:

                            bot.send_message(user, news_title + '\n' + news_link, reply_markup = markup_inline)

                        elif gmr == -1:
                            # Отправляем все новости, если юзер новый
                            bot.send_message(user, news_title + '\n' + news_link, reply_markup = markup_inline)
                        else:
                            # Сохраняем нерекомендуемую новость
                            save_last_ten_declined_news(news_title = news_title, news_link = news_link, user_id = user)

def start_sending():
    while True:

        try:
            send_last_news()
        except Exception as e:
            print('Ошибка, проверить: ',e)
            time.sleep(60)

        time.sleep(10)

thread1 = Thread(target=bot.infinity_polling)
thread2 = Thread(target=start_sending)
thread3 = Thread(target=start_schedule)

thread1.start()
thread2.start()
thread3.start()