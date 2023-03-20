# Переписать расписание на отдельный thread или закрывать threads 
# чтобы они не забивали память

import schedule
import time
import json
import threading

from reader_saver import save_last_news
from load_last_news import get_last_news_rbc, get_last_news_lenta, get_last_news_ria, get_last_news_habr
from prep_embeddings import save_embeddings
from model import train_model
from ddl import read_all_users

with open(f'./sources.json', 'w', encoding = 'utf-8') as f:

    data = {"list" : ["rbc","lenta","ria","habr"], 
    "list_russian" : ["РБК","Лента","РИА","Хабр"], 
    "mapping" : {"rbc" : "РБК", "lenta" : "Лента", "ria" : "РИА", "habr" : "Хабр"}}
    
    json.dump(data, f)

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def save_data_schedule():
    print("I'm running on thread %s" % threading.current_thread())
    try:
        save_last_news(get_last_news_rbc())
        save_embeddings(['rbc'])
    except:
        pass
    try:
        save_last_news(get_last_news_lenta())
        save_embeddings(['lenta'])
    except:
        pass
    try:
        save_last_news(get_last_news_ria())
        save_embeddings(['ria'])
    except:
        pass
    try:
        save_last_news(get_last_news_habr())
        save_embeddings(['habr'])
    except:
        pass

def train_models():
    print("I'm running on thread %s" % threading.current_thread())
    users = read_all_users()
    for user in users:
        train_model(user)
    print('Модели успешно обучились')

def start_schedule():
    schedule.every(1).minutes.do(run_threaded, save_data_schedule)
    schedule.every(12).hours.do(run_threaded, train_models)

    while True:
        schedule.run_pending()
        time.sleep(1)