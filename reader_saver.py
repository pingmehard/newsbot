import json
import hashlib
import os

def load_last_news(where_from):

    with open(f'./data/last_loaded_news_{where_from}.json', 'r') as f:
        load = json.load(f)

    news_hash = list(load.keys())[0]

    if f'last_news_{where_from}.json' not in os.listdir(os.getcwd() + '\\data\\'):

        data = {"last_hash" : news_hash}
        with open(f'./data/last_news_{where_from}.json', 'w') as f:
            json.dump(data, f)

        return 1, (news_hash, load[news_hash]['news_link'], load[news_hash]['news_title'], load[news_hash]['news_text'])
        
    else:
        with open(f'./data/last_news_{where_from}.json', 'r') as f:
            data = json.load(f)

    if news_hash != data["last_hash"]:
        data["last_hash"] = news_hash
        with open(f'./data/last_news_{where_from}.json', 'w') as f:
            json.dump(data, f)

        return 1, (news_hash, load[news_hash]['news_link'], load[news_hash]['news_title'], load[news_hash]['news_text'])
    else:
        return 0, None

def save_last_news(load):

    where_from, news_hash, news_link, news_title, news_text = load

    # Сохраняем в файл новости последней загрузки

    data = {news_hash : {'news_link' : news_link, 'news_title' : news_title, 'news_text' : news_text}}

    with open(f'./data/last_loaded_news_{where_from}.json', 'w') as f:
        json.dump(data, f)

    # Сохраняем в общий пул новостей

    if f'news_{where_from}.json' not in os.listdir(os.getcwd() + '\\data\\'):

        with open(f'./data/news_{where_from}.json', 'w') as f:
            json.dump(data, f)
    
    else:

        with open(f'./data/news_{where_from}.json', 'r') as f:
            data = json.load(f)

        data[news_hash] = {'news_link' : news_link, 'news_title' : news_title, 'news_text' : news_text}

        with open(f'./data/news_{where_from}.json', 'w') as f:
            json.dump(data, f)


def save_data(load):
    
    where_from, title, link, text = load

    json_file = {
        where_from: {
            'title': title,
            'link': link,
            'text': text,
            'hash': [str(hashlib.md5(i.encode()).hexdigest()) for i in link]
        }
    }

    with open(f'./data/{where_from}.json', 'w') as f:
        json.dump(json_file, f)
    
    print('File successfully saved')

def save_user_data(call_data):

    print(call_data)

    data = {call_data[2] : call_data[1]}

    if f'{call_data[0]}' not in os.listdir(os.getcwd() + f'\\data\\users\\'):

        os.makedirs(f'./data/users/{call_data[0]}')

        with open(f'./data/users/{call_data[0]}/{call_data[0]}.json', 'w') as f:
            json.dump(data, f)

    else:
        with open(f'./data/users/{call_data[0]}/{call_data[0]}.json', 'r') as f:
            data = json.load(f)

        data[call_data[2]] = call_data[1]

        with open(f'./data/users/{call_data[0]}/{call_data[0]}.json', 'w') as f:
            json.dump(data, f)

    print('User file successfully saved')

def save_last_ten_declined_news(user_id, news_title, news_link):

    data = {'news_list' : [{str(hashlib.md5(news_link.encode()).hexdigest()) : {'news_link' : news_link, 'news_title' : news_title}}]}

    if f'last_declined_news.json' not in os.listdir(os.getcwd() + f'\\data\\users\\{user_id}\\'):
        with open(f'./data/users/{user_id}/last_declined_news.json', 'w') as f:
            json.dump(data, f)
    else:
        with open(f'./data/users/{user_id}/last_declined_news.json', 'r') as f:
            data = json.load(f)

        if len(data['news_list']) < 10:
            data['news_list'].extend([{str(hashlib.md5(news_link.encode()).hexdigest()) : {'news_link' : news_link, 'news_title' : news_title}}])
        else:
            data['news_list'] = data['news_list'][1:]
            data['news_list'].extend([{str(hashlib.md5(news_link.encode()).hexdigest()) : {'news_link' : news_link, 'news_title' : news_title}}])

        with open(f'./data/users/{user_id}/last_declined_news.json', 'w') as f:
            json.dump(data, f)

def load_last_ten_declined_news(user_id):

    with open(f'./data/users/{user_id}/last_declined_news.json', 'r') as f:
        data = json.load(f)

    return data['news_list']