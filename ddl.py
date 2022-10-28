import requests
import telebot
import json
import datetime
import os
from telegram_bot_api_key import token

bot = telebot.TeleBot(token)

url = f'https://api.telegram.org/bot{token}/'

def get_updates():

    '''Возвращает обновления из чатов за последние 24 часа'''

    getUpdatesJson = requests.get(url + 'getUpdates').json()

    print('Got updates', datetime.datetime.now())

    return getUpdatesJson

def check_starts(getUpdatesJson):

    '''Возвращает список идентификаторов чатов, которые присоединились за последние 24 часа'''

    try:
        list_of_start_ids = list(set([i['message']['chat']['id'] for i in getUpdatesJson['result'] if 'message' in i]))
    except:
        list_of_start_ids = []

    return list_of_start_ids

def add_to_schedule(list_of_start_ids):

    if 'scheduler_users_list.json' not in os.listdir(os.getcwd()):

        json_file = {'users' : list_of_start_ids}

        with open(f'./scheduler_users_list.json', 'w') as f:
            json.dump(json_file, f)

    else:

        with open(f'./scheduler_users_list.json', 'r') as f:
            json_file = json.load(f)

        old_list_of_start_ids = json_file['users']

        list_of_start_ids.extend(old_list_of_start_ids)

        json_file = {'users' : list(set(list_of_start_ids))}

        with open(f'./scheduler_users_list.json', 'w') as f:
            json.dump(json_file, f)

    return f'Added {list(set(list_of_start_ids))} users to schedule'

def read_all_users():

    with open(f'./scheduler_users_list.json', 'r') as f:
        data = json.load(f)['users']

    return data

def send_message(chat_id, text):

    params = {'chat_id': chat_id, 'text': text}
    response = requests.post(url + 'sendMessage', data = params)

    return response

def cos_distance(a , b):
    '''Метрика косинусного расстояния'''
    try:
        return a@b/((a@a)*(b@b))**0.5
    except Exception as e:
        print(e)
        return -2

def log_errors(exception):
    with open('exceptions.txt', mode = 'a') as f:
        f.write(str(datetime.datetime.now()) + ' --------- \n' + str(exception))

def create_sources(user_id):

    with open(f'./sources.json', 'r') as f:
        sources = json.load(f)

    sources['target'] = {}

    for source in sources['list']:
        sources['target'][source] = 1

    with open(f'./data/users/{user_id}/sources.json', 'w') as f:
        json.dump(sources, f)

def read_sources(user_id):

    with open(f'./data/users/{user_id}/sources.json', 'r') as f:
        file = json.load(f)
        sources = [source for source in file['target'] if file['target'][source] == 1]

    return sources

def remove_sources(user_id, source):
    with open(f'./data/users/{user_id}/sources.json', 'r') as f:
        file = json.load(f)

    file['target'][source] = 0

    with open(f'./data/users/{user_id}/sources.json', 'w') as f:
        json.dump(file, f)

def add_sources(user_id, source):
    with open(f'./data/users/{user_id}/sources.json', 'r') as f:
        file = json.load(f)

    file['target'][source] = 1

    with open(f'./data/users/{user_id}/sources.json', 'w') as f:
        json.dump(file, f)

def negative_counter(user_id): # will be deprecated

    if 'negative_counter.json' in os.listdir(f'./data/users/{user_id}/'):
        with open(f'./data/users/{user_id}/negative_counter.json', 'r') as f:
            number = json.load(f)
        
        number = int(number) + 1

        with open(f'./data/users/{user_id}/negative_counter.json', 'w') as f:
            json.dump(number, f)

    else:
        with open(f'./data/users/{user_id}/negative_counter.json', 'w') as f:
            json.dump(1, f)

# def remove_from_schedule()