import schedule
import time
import json

from reader_saver import save_last_news
from load_last_news import get_last_news_rbc, get_last_news_lenta, get_last_news_ria, get_last_news_habr
from prep_embeddings import save_embeddings

with open(f'./sources.json', 'w', encoding = 'utf-8') as f:

    data = {"list" : ["rbc","lenta","ria","habr"], 
    "list_russian" : ["РБК","Лента","РИА","Хабр"], 
    "mapping" : {"rbc" : "РБК", "lenta" : "Лента", "ria" : "РИА", "habr" : "Хабр"}}
    
    json.dump(data, f)

def save_data_schedule():

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

schedule.every(1).minutes.do(save_data_schedule)

while True:
    schedule.run_pending()
    time.sleep(1)