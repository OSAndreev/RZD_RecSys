from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd


class ClusterSystem:
    def __init__(self):
        self.df = pd.read_csv('prepared_data.csv')
        self.df['smoking_attitude'] = self.df['smoking_attitude'].replace({1: 0, 2: 0, 3: 1, 4: 1, 5: 1})
        self.df.drop(columns=self.df.columns[0], axis=1, inplace=True)
        self.X = self.df.values[:, :]
        self.standard_scaler = StandardScaler()
        self.clus_dataset = self.standard_scaler.fit_transform(self.X)
        self.kmeans = KMeans(n_clusters=10, init='k-means++', random_state=42, n_init='auto')
        self.kmeans.fit_predict(self.clus_dataset)
        labels = self.kmeans.labels_
        self.df['cluster'] = labels

    def get_df(self):
        self.kmeans.fit_predict(self.clus_dataset)
        labels = self.kmeans.labels_
        self.df['cluster'] = labels
        return self.df

    def get_cluster(self, age, smoking_attitude, sociability, gender_male):
        "age: возраст; smoking_attitude: 1 - 5;\
            sociability: 1 - 5; gender_male: 0 - women, 1 - men"
        if smoking_attitude >= 3:
            smoking_attitude = 1
        else:
            smoking_attitude = 0
        new_user = np.array([[age, smoking_attitude, sociability, gender_male]])
        self.standard_scaler.fit(self.X)
        new_user_scaled = self.standard_scaler.transform(new_user)
        self.kmeans.fit(self.clus_dataset)
        cluster = self.kmeans.predict(new_user_scaled)
        self.clus_dataset = np.vstack((self.clus_dataset, new_user_scaled))
        self.X = np.vstack((self.X, new_user[0, :]))
        self.df.loc[len(self.df.index)] = [age, smoking_attitude, sociability, gender_male, cluster[0]]
        return cluster[0]


cs = ClusterSystem()


def get_cluster(age, smoking_attitude, sociability, gender_male):
    return cs.get_cluster(age, smoking_attitude, sociability, gender_male)


class Filtering():
    def __init__(self, user_item_matrix):
        self.user_item_matrix = user_item_matrix

    def calculate_user_similarity(self, collaborative=False):
        num_users, num_items = self.user_item_matrix.shape
        user_similarity = np.zeros((num_users, num_users))

        for i in range(num_users):
            for j in range(num_users):
                # Вычисляем косинусное сходство между пользователями i и j
                if collaborative and i == j:
                    continue
                dot_product = np.dot(self.user_item_matrix[i], self.user_item_matrix[j])
                norm_i = np.linalg.norm(self.user_item_matrix[i])
                norm_j = np.linalg.norm(self.user_item_matrix[j])

                if norm_i != 0 and norm_j != 0:
                    similarity = dot_product / (norm_i * norm_j)
                    user_similarity[i][j] = similarity

        return user_similarity

    # Расчет рекомендаций для конкретного пользователя
    def recommend(self, user_index, collaborative=False, num_recommends=0):
        user_similarity = self.calculate_user_similarity(collaborative=collaborative)
        num_users, num_items = self.user_item_matrix.shape
        scores = np.zeros(num_items)
        if not collaborative:
            num_recommends = num_items
        for item in range(num_items):
            if not collaborative or (collaborative and self.user_item_matrix[user_index][item] == 0):
                for other_user in range(num_users):
                    if (collaborative and other_user == user_index) or user_similarity[user_index][other_user] <= 0:
                        continue
                    scores[item] += user_similarity[user_index][other_user] * self.user_item_matrix[other_user][item]

        top_items_list = np.argsort(scores)[::-1]
        top_items_list.tolist()
        top_items = dict()
        for i in range(len(top_items_list)):
            if i < num_recommends:
                top_items[top_items_list[i]] = i
            else:
                top_items[top_items_list[i]] = 0
        return top_items

    def get_popular(self):
        num_users, num_items = self.user_item_matrix.shape
        scores = np.zeros(num_items)

        for item in range(num_items):
            for other_user in range(num_users):
                scores[item] += self.user_item_matrix[other_user][item]

        top_it = np.argsort(scores)[::-1]
        top_items_list = top_it.tolist()
        top_items = {top_items_list[i]: i for i in range(len(top_items_list))}

        return top_items


def get_history_filtering(top_or_bot_matrix, class_matrix, location_matrix, user_index):
    'Принимает на вход np-матрицы пользователь-предмет для 1) Нижних/верхних мест 2) \
    Классов вагонов мест 3) Локации мест и индекс пользователя в этих матрицах, \
    которому нужно сделать рекомендацию. Возвращает словарь, где ключи - фичи, \
    а значения - отранжированные значения индексов фич в матрице'

    class_filtering = Filtering(class_matrix)
    top_or_bot_filtering = Filtering(top_or_bot_matrix)
    location_filtering = Filtering(location_matrix)
    cls_list = class_filtering.recommend(user_index)
    cls = {cls_list[i]: i for i in range(len(cls_list))}
    tob_list = top_or_bot_filtering.recommend(user_index)
    tob = {tob_list[i]: i for i in range(len(tob_list))}
    loc_list = location_filtering.recommend(user_index)
    loc = {loc_list[i]: i for i in range(len(loc_list))}
    return {'class': cls, 'top_or_bot': tob, 'location': loc}


def get_collab_filtering(user_seats_matrix, user_index):
    'Принимает на вход матрицу пользователи - (номера мест, тип вагонов),\
     на пересечении - количество раз, которое пользователь брал место, и индекс юзера в матрице\
     важно, чтобы в матрице были только незанятые места в текущий момент. \
     '

    seats_filtering = Filtering(user_seats_matrix)
    seats = seats_filtering.recommend(user_index, collaborative=True, num_recommends=3)
    return seats


def get_popular_filtering(user_seats_matrix):
    'Принимает на вход матрицу пользователи - (номера мест, тип вагонов),\
    на пересечении - количество раз, которое пользователь брал место\
    важно, чтобы в матрице были только незанятые места в текущий момент. \
    Возвращает индекс наиболее подходящего места в матрице'
    seats_filtering = Filtering(user_seats_matrix)
    print(user_seats_matrix)
    seats = seats_filtering.get_popular()
    print('gpf', seats)
    return seats


def recommend(dict_of_dict: dict, pets=False, history=False, **kwargs):
    print(dict_of_dict)
    ranked_popular = kwargs.get('ranked_popular')
    print('first', ranked_popular[1])
    if history:
        ranked_class = kwargs.get('ranked_class')
        ranked_top_or_bot = kwargs.get('ranked_top_or_bot')
        ranked_location = kwargs.get('ranked_location')
        ranked_collaborative = kwargs.get('ranked_collaborative')
    seats = dict_of_dict.keys()
    print(seats)
    if history:
        first_seat = sorted(seats, key=lambda seat: (dict_of_dict[seat]['pets'] * pets,
                                                     -dict_of_dict[seat]['free_seats'],
                                                     ranked_class[dict_of_dict[seat]['seat_class']],
                                                     ranked_top_or_bot[dict_of_dict[seat]['bottom']],
                                                     ranked_location[dict_of_dict[seat]['location']],
                                                     -dict_of_dict[seat]['our_cluster'],
                                                     dict_of_dict[seat]['alien_cluster'],
                                                     ))[0]
        second_seat = sorted(seats, key=lambda seat: (dict_of_dict[seat]['pets'] * pets,
                                                      -dict_of_dict[seat]['free_seats'],
                                                      -dict_of_dict[seat]['our_cluster'],
                                                      dict_of_dict[seat]['alien_cluster'],
                                                      ))[:2]
        if second_seat[0] == first_seat:
            second_seat.pop(0)
        else:
            second_seat = second_seat[0]

        third_seat = sorted(seats, key=lambda seat: (dict_of_dict[seat]['pets'] * pets,
                                                     -dict_of_dict[seat]['free_seats'],
                                                     ranked_collaborative[seat],
                                                     -dict_of_dict[seat]['our_cluster'],
                                                     ))[:3]
        while (third_seat[0] == first_seat) or (third_seat[0] == second_seat):
            third_seat.pop(0)
        third_seat = third_seat[0]
    else:
        first_second_seat = sorted(seats, key=lambda seat: (dict_of_dict[seat]['pets'] * pets,
                                                            -dict_of_dict[seat]['free_seats'],
                                                            -dict_of_dict[seat]['our_cluster'],
                                                            dict_of_dict[seat]['alien_cluster'],
                                                            ranked_popular[seat],
                                                            ))[:2]
        first_seat = first_second_seat[0]
        second_seat = first_second_seat[1]
        third_seat = sorted(seats, key=lambda seat: (dict_of_dict[seat]['pets'] * pets,
                                                     -dict_of_dict[seat]['free_seats'],
                                                     ranked_popular[seat],
                                                     ))[:3]

        while (third_seat[0] == first_seat) or (third_seat[0] == second_seat):
            third_seat.pop(0)
        third_seat = third_seat[0]

    first_reason = []
    first_dict = dict_of_dict[first_seat]
    second_reason = []
    second_dict = dict_of_dict[second_seat]
    third_reason = []
    third_dict = dict_of_dict[third_seat]

    if history:
        if (first_dict['pets'] == False) and pets:
            first_reason.append('Без животных')
        if first_dict['free_seats'] > 0:
            first_reason.append('{0} свободных мест'.format(first_dict['free_seats']))
        if (ranked_class[first_dict['seat_class']] == 0) or (ranked_top_or_bot[first_dict['bottom']] == 0) or (
                ranked_location[first_dict['location']] == 0):
            first_reason.append('Основываясь на ваших предпочтениях')
        if first_dict['our_cluster'] > 0:
            first_reason.append('Подходящие вам попутчики')

        if (second_dict['pets'] == False) and pets:
            second_reason.append('Без животных')
        if second_dict['free_seats'] > 0:
            second_reason.append('{0} свободных мест'.format(second_dict['free_seats']))
        if second_dict['our_cluster'] > 0:
            second_reason.append('Подходящие вам попутчики')

        if (third_dict['pets'] == False) and pets:
            third_reason.append('Без животных')
        if third_dict['free_seats'] > 0:
            third_reason.append('{0} свободных мест'.format(third_dict['free_seats']))
        if ranked_collaborative[third_seat] <= 3:
            third_reason.append('Может быть интересно')
        if third_dict['our_cluster'] > 0:
            third_reason.append('Подходящие вам попутчики')
    else:
        if (first_dict['pets'] == False) and pets:
            first_reason.append('Без животных')
        if first_dict['free_seats'] > 0:
            first_reason.append('{0} свободных мест'.format(first_dict['free_seats']))
        if first_dict['our_cluster'] > 0:
            first_reason.append('Подходящие вам попутчики')
        if ranked_popular[first_seat] <= 3:
            first_reason.append('Часто выбирают')

        if (second_dict['pets'] == False) and pets:
            second_reason.append('Без животных')
        if second_dict['free_seats'] > 0:
            second_reason.append('{0} свободных мест'.format(second_dict['free_seats']))
        if second_dict['our_cluster'] > 0:
            second_reason.append('Подходящие вам попутчики')
        if ranked_popular[second_seat] <= 3:
            second_reason.append('Часто выбирают')

        if (third_dict['pets'] == False) and pets:
            third_reason.append('Без животных')
        if third_dict['free_seats'] > 0:
            third_reason.append('{0} свободных мест'.format(third_dict['free_seats']))
        if ranked_popular[third_seat] <= 3:
            third_reason.append('Часто выбирают')
    return [[first_seat, second_seat, third_seat], [first_reason, second_reason, third_reason]]


'''matrix = np.array([
    [0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1],
    [2, 3, 0, 0, 0, 0]
])
dict_of_dict = {41: {'pets': True, 'free_seats': 2, 'seat_class': 2, 'bottom': False,
                     'location': 'center', 'our_cluster': 2, 'alien_cluster': 2, 'seat_number': 20},
                13: {'pets': False, 'free_seats': 3, 'seat_class': 4, 'bottom': False,
                     'location': 'center', 'our_cluster': 1, 'alien_cluster': 2, 'seat_number': 22},
                15: {'pets': False, 'free_seats': 3 , 'seat_class': 4, 'bottom': True,
                     'location': 'left', 'our_cluster': 1, 'alien_cluster': 2, 'seat_number': 5}
                }
ranked_class = {1: 5, 2: 0, 3: 2, 4: 1, 5: 3, 6: 4, 7: 6}
ranked_top_or_bot = {True: 0, False: 1}
ranked_location = {'right': 0, 'left': 1, 'center': 2}
ranked_collaborative = {41: 0, 13: 1, 15: 22, 18: 5}
ranked_popular = {41: 2, 13: 0, 15: 22, 18: 5}

print(ranking(dict_of_dict, pets=True, history=True, ranked_popular=ranked_popular,
              ranked_class=ranked_class, ranked_top_or_bot=ranked_top_or_bot,
              ranked_location=ranked_location, ranked_collaborative=ranked_collaborative))
# print(get_collab_filtering(matrix, 0))'''
