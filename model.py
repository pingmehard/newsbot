from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from ddl import cos_distance

import json
import numpy as np
import pandas as pd

from tensorflow import keras
from tensorflow.keras import layers

def train_model(user_id, sources):

    data_vectors = {}
    matching_cos_distance = []
    potential_positive_samples = []

    # Загружаем все новости в оперативку
    for where_from in sources:
        with open(f'./data/vectors/vectors_news_{where_from}.json', 'r') as f:
            temp = json.load(f)
            for i in temp:
                data_vectors[i] = temp[i]

    # Открываем все реакции человека на новости
    with open(f'./data/users/{user_id}/embeddings_{user_id}.json', 'r') as f:
        data = json.load(f)

    # Находим отличия от отрицальных новостей 
    negative_set = [id for id in data.keys() if data[id]['target'] == '0']
    all_set = set(data_vectors.keys())
    not_negative_set = all_set ^ set(negative_set)

    print(len(negative_set), len(not_negative_set))

    # Сравнение потенциальных положительных новостей со всеми новостями, поиск самых близких негативных к ним
    c = 0
    for id in negative_set:
        for id_all in not_negative_set:
            matching_cos_distance.append(cos_distance(np.array(data_vectors[id]['news_embedding']), np.array(data_vectors[id_all]['news_embedding'])))
            potential_positive_samples.append(id_all)

            c += 1
            if c % 1_000_000 == 0:
                print(c, end = '\r')

    # Определяем позитивные новости из существующей разметки пользователя
    positive_samples = []
    positive_set = [id for id in data.keys() if data[id]['target'] == '1']

    negative_list_std = []

    # Считаем отклонение для определения параметра отбора позитивных новостей, которые понравились
    matching_std = np.std(matching_cos_distance)
    matching_mean = np.mean(matching_cos_distance)

    # Ищем позитивные для человека новости, потенциально это все новости, что меньше (среднее по всем сравнениям + 1 стандартное отклонение)
    for item in zip(potential_positive_samples, matching_cos_distance):
        if item[1] >= (matching_mean + 2 * matching_std):
            negative_list_std.append(item[0])

    # Вычитаем из позитивных потенциальных негативные относительно стандартного отклонения
    positive_samples = set(potential_positive_samples) - set(negative_list_std)
    # Расширяем сет размеченных позитивных позитивными потенциально
    positive_set.extend(positive_samples)

    # Сколько позитивных у нас получилось
    print(len(positive_set))
    # Проверяем, есть ли у нас пересечения между позитивными и негативными (не должно быть совсем)
    print(len(set(negative_list_std) & set(positive_set)))

    # Получаем эмбеддинги каждого позитивного и негативного случая
    positive_embeddings = []
    negative_embeddings = []

    for id in positive_set:
        positive_embeddings.append(data_vectors[id]['news_embedding'])

    for id in set(negative_list_std):
        negative_embeddings.append(data_vectors[id]['news_embedding'])

    # Превращаем в numpy все вектора позитивных и отрциательных новостей

    positive_embeddings_array = np.array(positive_embeddings)
    negative_embeddings_array = np.array(negative_embeddings)

    # Смотрим какой shape для каждого
    print(positive_embeddings_array.shape, negative_embeddings_array.shape)

    # Заполняем 0 и 1 каждый из отрицательных и положительных новостей
    ones_array = np.ones((positive_embeddings_array.shape[0],1))
    zeros_array = np.zeros((negative_embeddings_array.shape[0],1))

    # Собираем все воедино в датасет
    a = np.hstack((positive_embeddings_array, ones_array))
    b = np.hstack((negative_embeddings_array, zeros_array))
    X_np = np.vstack((a, b))

    # Затем обучаем модель искать такие или относить к негативным все остальные новости
    X_df = pd.DataFrame(X_np).rename({300:'target'}, axis = 1)

    # Получаем количество сэмплов для разделения наибольшего класса

    n_splits = X_df['target'].value_counts()[0] // X_df['target'].value_counts()[1]

    X_df['splits'] = X_df.index % n_splits

    target_0 = X_df[(X_df['target'] == 0)].sample(n = X_df['target'].value_counts()[1], axis = 0)
    target_1 = X_df[X_df['target'] == 1]

    target_sampled = pd.concat([target_0, target_1], axis = 0)

    y = target_sampled['target']
    X = target_sampled.drop(['target', 'splits'], axis = 1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = keras.Sequential(
        [   
            layers.Dense(128, activation="relu"),
            layers.Dense(32, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(loss="binary_crossentropy", optimizer = keras.optimizers.Adam(learning_rate=0.0001), metrics=[tf.keras.metrics.BinaryAccuracy()])

    model.fit(X_train, y_train, epochs=50, batch_size = 32, validation_data=(X_test, y_test))

    preds_sigm = model.predict(X_test)
    preds = (preds_sigm >= 0.5) * 1

    print(classification_report(y_test, preds))

    # Сохраняем все обученные модели

    model.save(f'./data/users/{user_id}/model')

    print('Модель успешно сохранена')

def predict(user_id, embedding):

    model = keras.models.load_model(f'./data/users/{user_id}/model')

    return model.predict(embedding)