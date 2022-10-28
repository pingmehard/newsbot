import os, json
import numpy as np

from razdel import tokenize
from ddl import cos_distance
from navec import Navec

import nltk
from nltk.corpus import stopwords

from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    PER,
    NamesExtractor,

    Doc
)

segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)
names_extractor = NamesExtractor(morph_vocab)

nltk.download('stopwords')
stops = set(stopwords.words('russian'))

path = r".\data\vectors\navec_news_v1_1B_250K_300d_100q.tar"  # 51MB
navec = Navec.load(path)  # ~1 sec, ~100MB RAM

with open(f'./sources.json', 'r', encoding = 'utf-8') as f:
    sources = json.load(f)['list']

def get_tokens(string):
    tokens = list(tokenize(string))
    return [_.text for _ in tokens]

def to_navec(phrase):

    phrase_low = phrase.lower()
    tokens = get_tokens(phrase_low)

    s = navec.get('<pad>')

    for tok in tokens:
        if tok in navec:
            s += navec.get(tok)
        else:
            s += navec.get('<unk>')

    return s

def lem_tokens(string):
    doc = Doc(string)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
    return [_.lemma for _ in doc.tokens]

def delete_stop_words(words_list):
    return [word for word in words_list if word not in stops]     


def save_embeddings(sources):

    for where_from in sources:

        with open(f'./data/news_{where_from}.json', 'r', encoding="utf-8") as f:
            data = json.load(f)

        if f'vectors_news_{where_from}.json' not in os.listdir(os.getcwd() + '\\data\\vectors\\'):

            for id in data:
                data[id]['news_embedding'] = to_navec(data[id]['news_title']).tolist()
                data[id].pop('news_link', None)
                data[id].pop('news_text', None)

            with open(f'./data/vectors/vectors_news_{where_from}.json', 'w') as f:
                json.dump(data, f)

        else:

            with open(f'./data/vectors/vectors_news_{where_from}.json', 'r') as f:
                data_vectors = json.load(f)

            news_hashes = list(data_vectors.keys())

            for id in data:
                if id not in news_hashes:
                    data_vectors[id] = {'news_embedding':to_navec(data[id]['news_title']).tolist()}

            with open(f'./data/vectors/vectors_news_{where_from}.json', 'w') as f:
                json.dump(data_vectors, f)

def create_user_embeddings(user_id):

    with open(f'./data/users/{user_id}/{user_id}.json', 'r') as f:
        data = json.load(f)
    
    data_vectors = {}

    for where_from in sources:
        with open(f'./data/vectors/vectors_news_{where_from}.json', 'r') as f:
            temp = json.load(f)
            for i in temp:
                data_vectors[i] = temp[i]

    for id in data:
        data[id] = {'news_embedding' : data_vectors[id]['news_embedding'], 'target' : data[id]}

    with open(f'./data/users/{user_id}/embeddings_{user_id}.json', 'w') as f:
        json.dump(data, f)
    
def get_message_rule(news_title, user_id):

    if f'{user_id}' in os.listdir(os.getcwd() + f'\\data\\users\\'):

        with open(f'./data/users/{user_id}/embeddings_{user_id}.json', 'r') as f:
            data = json.load(f)

        news_title_emb = to_navec(news_title)

        for id in data:
            data[id]['cos_distance'] = cos_distance(np.array(data[id]['news_embedding']), news_title_emb)

        news_cos_distances = [data[id]['cos_distance'] for id in data if data[id]['target'] == '0']

        for i in news_cos_distances:
            if i > 0.65:
                return 0, None
        return 1, news_title_emb

    else:
        return -1, None

def find_intersections(news_title, user_id, news_title_emb):

    with open(f'./data/users/{user_id}/embeddings_{user_id}.json', 'r') as f:
        data = json.load(f)

    for id in data:
        data[id]['cos_distance'] = cos_distance(np.array(data[id]['news_embedding']), news_title_emb)

    news_cos_distances = [(id, data[id]['cos_distance']) for id in data if data[id]['target'] == '0']

    data_temp = {}
    for where_from in sources:

        with open(f'./data/news_{where_from}.json', 'r', encoding="utf-8") as f:
            data = json.load(f)
        for news in data:
            data_temp[news] = data[news]

    top_10_titles = [data_temp[i[0]]['news_title'] for i in sorted(news_cos_distances, key = lambda x: x[1])[::-1][:10]]

    array_temp = []
    dict_temp = {}

    news_title_ready = delete_stop_words(lem_tokens(news_title))

    for i in top_10_titles:
        array_temp.extend(list(np.intersect1d(delete_stop_words(lem_tokens(i)), news_title_ready)))
    for i in array_temp:
        if i not in dict_temp:
            dict_temp[i] = 1
        else:
            dict_temp[i] += 1

    for i in dict_temp:
        if dict_temp[i] >= 3:
            return 0, i
    return 1, None