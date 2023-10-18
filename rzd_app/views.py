from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .fill_database import *
from .forms import *
import numpy as np
from .RecSys import *
from .fill_passengers_seats import *


def start_page(request):
    fill_database_van_character()
    fill_database_train()
    fill_database_van()

    return render(request, 'start_page.html')


def login_page(request):
    return HttpResponse('Логин')


def register_page(request):
    return HttpResponse('Регистрация')


class RegisterUserView(CreateView):
    model = User
    template_name = 'register_page.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('create_user')
    success_msg = "Пользователь успешно создан"

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        login(self.request, user)  # Авторизация пользователя
        return response


class LoginUserView(LoginView):
    template_name = "login_page.html"
    form_class = AuthUserForm
    success_url = reverse_lazy('main_page')

    def get_success_url(self):
        return self.success_url


def create_user(request):
    error = ''
    if request.method == 'POST':
        form = PassengerForm(request.POST)
        if form.is_valid():
            created_user = form.save(commit=False)
            created_user.django_user = get_object_or_404(User, id=request.user.id)
            created_user.cluster = get_cluster(created_user.age, created_user.smoking_attitude,
                                               created_user.sociability, created_user.gender)
            created_user.save()
            return redirect('main_page')
        else:
            error = 'Форма была неверной'
    form = PassengerForm()
    data = {
        'form': form,
        'error': error
    }
    return render(request, 'create_user.html', data)


def main_page(request):

    check_fill_seats()
    #fill_passengers_seats(Train.objects.get(id=1))
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)

    # user_obj.cluster = get_cluster(user_obj.age,user_obj.smoking_attitude, user_obj.sociability, user_obj.gender)
    # user_obj.save() - ЗАПИСЫВАЕТ КЛАСТЕРЫ В БД ПРИ АВТОРИЗАЦИИ (ДЛЯ АККОВ КОТОРЫЕ БЫЛИ СОЗДАНЫ РАНЬШЕ ДОБАВЛЕНИЯ АТРИБУТА)
    # print(class_matrix())
    # top_bot_m()
    # user_seats_matrix()
    trains = Train.objects.all()
    error = ''
    if request.method == 'POST':
        form = ChildrenAnimalsForm(request.POST)
        if form.is_valid():
            user_obj.trip_with_animals = form.cleaned_data.get('trip_with_animals')
            user_obj.trip_with_child = form.cleaned_data.get('trip_with_child')
            user_obj.save()
            return redirect('main_page')
        else:
            HttpResponse('Где-то накосячили..')
    else:
        form = ChildrenAnimalsForm(instance=user_obj)

    data = {
        "user": user_obj,
        "train": trains,
        "form": form
    }
    return render(request, 'main_page.html', context=data)


def check_fill_seats():
    vans = list(obj for obj in Van.objects.values_list('id', 'train', 'character'))
    seats = list(obj for obj in Seat.objects.values_list('id'))
    if seats == []:
        for j in vans:
            if j[2] == 1:
                for i in range(0, 54):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=2800, seat_number=i + 1)
                    seat.save()
            elif j[2] == 2:
                for i in range(0, 54):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=3000, seat_number=i + 1)
                    seat.save()
            elif j[2] == 3:
                for i in range(0, 36):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=4000, seat_number=i + 1)
                    seat.save()
            elif j[2] == 4:
                for i in range(0, 36):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=4500, seat_number=i + 1)
                    seat.save()
            elif j[2] == 5:
                for i in range(0, 18):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=5000, seat_number=i + 1)
                    seat.save()
            elif j[2] == 6:
                for i in range(0, 18):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=4800, seat_number=i + 1)
                    seat.save()
            elif j[2] == 7:
                for i in range(0, 12):
                    seat = Seat.objects.create(van=Van.objects.get(id=j[0]), price=14000, seat_number=i + 1)
                    seat.save()


def route_page(request, pk=''):
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)
    train = Train.objects.get(id=pk)
    vans = Van.objects.filter(train=train)
    if Trip.objects.filter(finished=False, passenger=user_obj).exists():
        trip = Trip.objects.filter(finished=False, passenger=user_obj)[0]
        animals = trip.with_animals
    else:
        animals = user_obj.trip_with_animals

    # Место для рекомендаций

    passengers = Passenger.objects.all()
    user_cluster = get_cluster(user_obj.age, user_obj.smoking_attitude, user_obj.sociability, user_obj.gender)

    # print(main_dict(train, user_obj)) #Рассматривает все свободные места в выбранном поезде

    if Trip.objects.filter(finished=True, passenger=user_obj).exists():
        history = True
    else:
        history = False
    top_or_bot_matrix = top_bot_m()
    class_mx = class_matrix()
    loc_m = location_matrix()

    user_seats_m = user_seats_matrix()
    dict_of_dict = main_dict(train, user_obj)

    pre_ranked_popular = get_popular_filtering(user_seats_m)
    ranked_popular = {get_seat(id): pre_ranked_popular[id] for id in pre_ranked_popular.keys()}
    if history:
        history_filtering = get_history_filtering(top_or_bot_matrix, class_matrix=class_mx,
                                                  location_matrix=loc_m, user_index=user_obj.id)

        pre_ranked_class = history_filtering['class']
        ranked_class = {get_class(id): pre_ranked_class[id] for id in pre_ranked_class.keys()}

        pre_ranked_top_or_bot = history_filtering['top_or_bot']
        ranked_top_or_bot = {get_bottom(id): pre_ranked_top_or_bot[id] for id in pre_ranked_top_or_bot.keys()}

        pre_ranked_location = history_filtering['location']
        ranked_location = {get_location(id): pre_ranked_location[id] for id in pre_ranked_location.keys()}

        pre_ranked_collaborative = get_collab_filtering(user_seats_m, user_index=user_obj.id)
        ranked_collaborative = {get_seat(id): pre_ranked_collaborative[id] for id in pre_ranked_collaborative.keys()}

        recs = recommend(dict_of_dict, pets=animals, history=history,
                         ranked_popular=ranked_popular, ranked_class=ranked_class,
                         ranked_top_or_bot=ranked_top_or_bot, ranked_location=ranked_location,
                         ranked_collaborative=ranked_collaborative)
    else:
        recs = recommend(dict_of_dict, pets=animals, history=history,
                         ranked_popular=ranked_popular)

    plac = vans.filter(character__in=[1, 2])
    coupe = vans.filter(character__in=[3, 4])
    sv = vans.filter(character__in=[5, 6])
    lux = vans.filter(character=7)
    if list(plac.values_list('id')) == []:
        plac = None
    if list(coupe.values_list('id')) == []:
        coupe = None
    if list(sv.values_list('id')) == []:
        sv = None
    if list(lux.values_list('id')) == []:
        lux = None

    seat1 = Seat.objects.get(id=recs[0][0])
    seat2 = Seat.objects.get(id=recs[0][1])
    seat3 = Seat.objects.get(id=recs[0][2])


    return render(request, 'route_page.html', context={
        'plac': plac,
        'coupe': coupe,
        'sv': sv,
        'lux': lux,
        'train': train,
        'user': user_obj,
        'recs_1': seat1,
        'recs_2': seat2,
        'recs_3': seat3,
        'reason_1':recs[1][0],
        'reason_2': recs[1][1],
        'reason_3': recs[1][2]
    })


def get_seat_near(seat_id):
    # Принимает место и возвращает айди всех мест рядом
    seat = Seat.objects.get(id=seat_id)
    van = seat.van
    seat_quantity = van.character.seat_quantity
    neighbour_seat = []

    if van.character.type == 1:
        van_blocks = [[1, 2, 3, 4, 54, 53], [5, 6, 7, 8, 52, 51], [9, 10, 11, 12, 50, 49],
                      [13, 14, 15, 16, 48, 47], [17, 18, 19, 20, 46, 45], [21, 22, 23, 24, 44, 43],
                      [25, 26, 27, 28, 42, 41], [29, 30, 31, 32, 40, 39], [33, 34, 35, 36, 38, 37]]
        for i in van_blocks:
            if seat.seat_number in i:
                for j in i:
                    if seat.seat_number != j:
                        this_seat = Seat.objects.filter(van=van, seat_number=j)

                        neighbour_seat.append(list(this_seat.values_list('id'))[0][0])
                return neighbour_seat
    if van.character.type == 2:
        van_blocks = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12],
                      [13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24],
                      [25, 26, 27, 28], [29, 30, 31, 32], [33, 34, 35, 36]]
        for i in van_blocks:
            if seat.seat_number in i:
                for j in i:
                    if seat.seat_number != j:
                        this_seat = Seat.objects.filter(van=van, seat_number=j)
                        neighbour_seat.append(list(this_seat.values_list('id'))[0][0])
                return neighbour_seat
    if van.character.type == 3:
        van_blocks = [[1, 2], [3, 4], [5, 6],
                      [7, 8], [9, 10], [11, 12],
                      [13, 14], [15, 16], [17, 18]]
        for i in van_blocks:
            if seat.seat_number in i:
                for j in i:
                    if seat.seat_number != j:
                        this_seat = Seat.objects.filter(van=van, seat_number=j)
                        neighbour_seat.append(list(this_seat.values_list('id'))[0][0])
                return neighbour_seat
    if van.character.type == 4:
        van_blocks = [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]]
        for i in van_blocks:
            if seat.seat_number in i:
                for j in i:
                    if seat.seat_number != j:
                        this_seat = Seat.objects.filter(van=van, seat_number=j)
                        neighbour_seat.append(list(this_seat.values_list('id'))[0][0])
                return neighbour_seat


def main_dict(train, user):
    vans = Van.objects.filter(train=train)
    seats = Seat.objects.all()
    trips = Trip.objects.filter(finished=False)

    m_dict = {}
    for van in vans:
        for s in seats.filter(van=van):
                key = 0
                for t in trips:
                    if t.seats == s:
                        key = 1
                        break
                else:
                    seat_id = s.id
                    # проверка на животных
                    pet = False
                    block = get_seat_near(seat_id)
                    block.append(seat_id)
                    free_count = 0
                    for t in trips:
                        for i in block:
                            if t.seats.id == i and i != block[:-1]:
                                free_count += 1
                            if t.seats.id == i and t.with_animals:
                                pet = True



                    #проверка свободных мест



                    #проверка класса сиденья
                    seat_class = van.character.class_van
                    #нижняя койка, да или нет

                    bottom = False
                    if s.seat_number % 2 != 0 or van.character.type == 3:
                        bottom = True
                    #определяем где в вагоне находится
                    position = 0
                    location = ''
                    if s.van.character.type == 1:
                        van_blocks = [[1, 2, 3, 4, 54, 53], [5, 6, 7, 8, 52, 51], [9, 10, 11, 12, 50, 49],
                                      [13, 14, 15, 16, 48, 47], [17, 18, 19, 20, 46, 45], [21, 22, 23, 24, 44, 43],
                                      [25, 26, 27, 28, 42, 41], [29, 30, 31, 32, 40, 39], [33, 34, 35, 36, 38, 37]]

                        for i in range(len(van_blocks)):
                            if s.seat_number in van_blocks[i]:
                                position = i
                                break

                        if position <= 3:
                            location = 'left'
                        elif position <= 6:
                            location = 'center'
                        else:
                            location = 'right'

                    if s.van.character.type == 2:
                        van_blocks = [[1,2,3,4], [5,6,7,8], [9,10,11,12],
                              [13,14,15,16], [17,18,19,20], [21,22,23, 24],
                              [25, 26, 27, 28], [29,30,31,32], [33,34,35,36]]

                        for i in range(len(van_blocks)):
                            if s.seat_number in van_blocks[i]:
                                position = i
                                break

                        if position <= 3:
                            location = 'left'
                        elif position <= 6:
                            location = 'center'
                        else:
                            location = 'right'

                    if s.van.character.type == 3:
                        van_blocks = [[1,2], [3,4], [5,6],
                              [7,8], [9,10], [11,12],
                              [13,14], [15,16], [17,18]]

                        for i in range(len(van_blocks)):
                            if s.seat_number in van_blocks[i]:
                                position = i
                                break
                        if position <= 3:
                            location = 'left'
                        elif position <= 6:
                            location = 'center'
                        else:
                            location = 'right'
                    if s.van.character.type == 4:
                        van_blocks = [[1,2], [3,4], [5,6], [7,8], [9,10], [11,12]]

                        for i in range(len(van_blocks)):
                            if s.seat_number in van_blocks[i]:
                                position = i
                                break
                        if position <= 2:
                            location = 'left'
                        elif position <= 4:
                            location = 'center'
                        else:
                            location = 'right'

                    #our cluster
                    block_clustering = []
                    our_cluster = user.cluster
                    for i in block:
                        for t in trips:
                            pass_seat = Seat.objects.get(id=i)
                            if t.seats == pass_seat:
                                user_obj = t.passenger
                                block_clustering.append(user_obj.cluster)
                    clust_counter = 0
                    not_our_cluster = 0
                    for j in block_clustering:

                        if j == our_cluster:
                            clust_counter += 1
                        elif j != our_cluster:

                            not_our_cluster += 1

                    seat_number = s.seat_number

                    m_dict[seat_id] = {'pets': pet,
                                               'free_seats': len(block)-free_count-1,
                                               'seat_class': seat_class,
                                                'bottom': bottom,
                                               'location': location,
                                               'our_cluster': clust_counter,
                                                'alien_cluster': not_our_cluster,
                                               'seat_number': seat_number}
    return m_dict


def van_page(request, pk=''):
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)
    trips = Trip.objects.filter(finished=False)

    van = Van.objects.get(id=pk)
    seat_quantity = van.character.seat_quantity
    seat_list = [0] * seat_quantity
    trip_list = [None] * seat_quantity
    neighbours = [None] * seat_quantity
    seat_numbers = [i + 1 for i in range(0, seat_quantity)]
    ticket_purchased = False

    for s in trips:
        if s.seats.van == van:
            if s.passenger == user_obj:
                ticket_purchased = True
            seat_list[s.seats.seat_number - 1] = 1
            neighbours[s.seats.seat_number - 1] = s.passenger
            trip_list[s.seats.seat_number - 1] = s

    # print(neighbours)

    if van.character.class_van <= 2:
        # print(seat_numbers)
        seat_top = []
        seat_top_took = []
        seat_bottom = []
        seat_bottom_took = []
        seat_side = []
        seat_side_took = []
        for i in seat_numbers:
            if i % 2 == 0 and i <= 36:
                seat_top.append(i)
                seat_top_took.append(seat_list[i - 1])
            elif i % 2 != 0 and i <= 36:
                seat_bottom.append(i)
                seat_bottom_took.append(seat_list[i - 1])
            else:
                seat_side.append(i)
                seat_side_took.append(seat_list[i - 1])
        # print(seat_top_took)
        # print(seat_bottom_took)
        # print(seat_side_took)
        data = {
            'seat_numbers': zip(seat_numbers, neighbours, trip_list),
            'seat_top': zip(seat_top, seat_top_took),
            'seat_bottom': zip(seat_bottom, seat_bottom_took),
            'seat_side': zip(seat_side[::-1], seat_side_took[::-1]),
            'van': van,
            'van_ch': van.character,
            'price': Seat.objects.filter(van=van)[0].price,
            'user': user_obj,
            'phone_view': ticket_purchased

        }

    elif van.character.class_van <= 4:
        seat_top = []
        seat_top_took = []
        seat_bottom = []
        seat_bottom_took = []
        for i in seat_numbers:
            if i % 2 == 0:
                seat_top.append(i)
                seat_top_took.append(seat_list[i - 1])
            elif i % 2 != 0:
                seat_bottom.append(i)
                seat_bottom_took.append(seat_list[i - 1])

        data = {
            'seat_numbers': zip(seat_numbers, neighbours, trip_list),
            'seat_top': zip(seat_top, seat_top_took),
            'seat_bottom': zip(seat_bottom, seat_bottom_took),
            'van': van,
            'van_ch': van.character,
            'price': Seat.objects.filter(van=van)[0].price,
            'user': user_obj,
            'phone_view': ticket_purchased
        }
    elif van.character.class_van <= 6:
        data = {
            'seat_numbers': zip(seat_numbers, neighbours, trip_list),
            'seat_bottom': zip(seat_numbers, seat_list),
            'van': van,
            'van_ch': van.character,
            'price': Seat.objects.filter(van=van)[0].price,
            'user': user_obj,
            'phone_view': ticket_purchased
        }
    elif van.character.class_van == 7:
        seat_top = []
        seat_top_took = []
        seat_bottom = []
        seat_bottom_took = []
        for i in seat_numbers:
            if i % 2 == 0:
                seat_top.append(i)
                seat_top_took.append(seat_list[i - 1])
            elif i % 2 != 0:
                seat_bottom.append(i)
                seat_bottom_took.append(seat_list[i - 1])

        data = {
            'seat_numbers': zip(seat_numbers, neighbours, trip_list),
            'seat_top': zip(seat_top, seat_top_took),
            'seat_bottom': zip(seat_bottom, seat_bottom_took),
            'van': van,
            'van_ch': van.character,
            'price': Seat.objects.filter(van=van)[0].price,
            'user': user_obj,
            'phone_view': ticket_purchased
        }

    return render(request, 'van_page.html', context=data)


def buy_ticket(request, tr='', vn='', st=''):
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)

    van = Van.objects.get(train=tr, id=vn)
    seats = Seat.objects.get(van=van, seat_number=st)
    trip = Trip.objects.create(passenger=user_obj, seats=seats, finished=False, with_children=user_obj.trip_with_child,
                               with_animals=user_obj.trip_with_animals)
    user_obj.trip_with_child = 0
    user_obj.trip_with_animals = False
    user_obj.save()

    trip.save()

    return redirect('van_page', pk=vn)


def reject_ticket(request, tr='', vn='', st='', id=''):
    if id != '':
        Trip.objects.get(id=id).delete()
        return redirect('my_trips')
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)

    van = Van.objects.get(train=tr, id=vn)
    seats = Seat.objects.get(van=van, seat_number=st)

    Trip.objects.filter(passenger=user_obj, seats=seats, finished=False).delete()
    # TODO поля пользователя trip_with_animals и trip_with_child вернуть к дефолту
    return redirect('van_page', pk=vn)


def my_trips(request):
    user_id = get_object_or_404(User, id=request.user.id)
    user_obj = Passenger.objects.get(django_user=user_id)

    active_trips = Trip.objects.filter(passenger=user_obj, finished=False)
    finished_trips = Trip.objects.filter(passenger=user_obj, finished=True)
    if list(finished_trips.values_list('id')) == []:
        finished_trips = None
    if list(active_trips.values_list('id')) == []:
        active_trips = None
    data = {
        'active': active_trips,
        'finished': finished_trips
    }
    return render(request, 'my_trips.html', context=data)


##########################################

def top_bot_m():
    trips = Trip.objects.filter(finished=True)
    passengers = Passenger.objects.all()
    top_count = 0
    bottom_count = 0
    string = []
    min_id = 10 ** 10
    for p in passengers:
        if p.id < min_id:
            min_id = p.id

        top_count = 0
        bottom_count = 0
        for t in trips.filter(passenger=p):
            if t.seats.seat_number % 2 == 0:
                top_count += 1
            else:
                bottom_count += 1
        string.append([top_count, bottom_count])

    array = [[0, 0] for i in range(min_id)] + string

    top_or_bot_matrix = np.array(array)
    return top_or_bot_matrix


def get_bottom(id):
    if id == 0:
        return False
    else:
        return True


def location_matrix():
    passengers = Passenger.objects.all()
    trips = Trip.objects.filter(finished=True)
    left_count = 0
    center_count = 0
    right_count = 0
    location = ''
    string = []
    min_id = 10 ** 10
    for p in passengers:
        if p.id < min_id:
            min_id = p.id
        left_count = 0
        center_count = 0
        right_count = 0
        location = 'none'
        for t in trips.filter(passenger=p):
            s = t.seats
            s_number = s.seat_number
            if s.van.character.type == 1:
                van_blocks = [[1, 2, 3, 4, 54, 53], [5, 6, 7, 8, 52, 51], [9, 10, 11, 12, 50, 49],
                              [13, 14, 15, 16, 48, 47], [17, 18, 19, 20, 46, 45], [21, 22, 23, 24, 44, 43],
                              [25, 26, 27, 28, 42, 41], [29, 30, 31, 32, 40, 39], [33, 34, 35, 36, 38, 37]]

                for i in range(len(van_blocks)):
                    if s.seat_number in van_blocks[i]:
                        position = i
                        break

                if position <= 3:
                    location = 'left'
                elif position <= 6:
                    location = 'center'
                else:
                    location = 'right'

            if s.van.character.type == 2:
                van_blocks = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12],
                              [13, 14, 15, 16], [17, 18, 19, 20], [21, 22, 23, 24],
                              [25, 26, 27, 28], [29, 30, 31, 32], [33, 34, 35, 36]]

                for i in range(len(van_blocks)):
                    if s.seat_number in van_blocks[i]:
                        position = i
                        break

                if position <= 3:
                    location = 'left'
                elif position <= 6:
                    location = 'center'
                else:
                    location = 'right'

            if s.van.character.type == 3:
                van_blocks = [[1, 2], [3, 4], [5, 6],
                              [7, 8], [9, 10], [11, 12],
                              [13, 14], [15, 16], [17, 18]]

                for i in range(len(van_blocks)):
                    if s.seat_number in van_blocks[i]:
                        position = i
                        break
                if position <= 3:
                    location = 'left'
                elif position <= 6:
                    location = 'center'
                else:
                    location = 'right'
            if s.van.character.type == 4:
                van_blocks = [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]]

                for i in range(len(van_blocks)):
                    if s.seat_number in van_blocks[i]:
                        position = i
                        break
                if position <= 2:
                    location = 'left'
                elif position <= 4:
                    location = 'center'
                else:
                    location = 'right'

            if location == 'left':
                left_count += 1
            elif location == 'right':
                right_count += 1
            elif location == 'center':
                center_count += 1
        string.append([left_count, center_count, right_count])

    array = [[0, 0, 0] for i in range(min_id)] + string

    location_matrix = np.array(array)
    return location_matrix


def get_location(id):
    if id == 0:
        return 'left'
    elif id == 1:
        return 'center'
    elif id == 2:
        return 'right'


def class_matrix():
    trips = Trip.objects.filter(finished=True)
    passengers = Passenger.objects.all()

    string = []
    min_id = 10 ** 10
    for p in passengers:
        if p.id < min_id:
            min_id = p.id
        one = 0
        two = 0
        three = 0
        four = 0
        five = 0
        six = 0
        seven = 0
        for t in trips.filter(passenger=p):
            v = t.seats.van.character.class_van
            if v == 1:
                one += 1
            elif v == 2:
                two += 1
            elif v == 3:
                three += 1
            elif v == 4:
                four += 1
            elif v == 5:
                five += 1
            elif v == 6:
                six += 1
            elif v == 7:
                seven += 1
        string.append([one, two, three, four, five, six, seven])

    array = [[0, 0, 0, 0, 0, 0, 0] for i in range(min_id)] + string

    class_matrix = np.array(array)
    return class_matrix


def get_class(id):
    return id + 1

def user_seats_matrix():
    passengers = Passenger.objects.all()
    seats = Seat.objects.all()
    trips_now = Trip.objects.filter(finished=False)
    trips = Trip.objects.filter(finished=True)
    free_seats = []
    string =[]
    all_seats = []
    all_seats_val = []
    min_id = 10**10

    for s in seats:
        all_seats.append(s.id)
        all_seats_val.append(0)

    key = 0
    temp_arr = [i for i in range(min(all_seats))]
    temp_arr_val = [0 for j in range(min(all_seats))]

    all_seats = temp_arr + all_seats

    all_seats_val = temp_arr_val + all_seats_val +[0]

    for j in all_seats:
        key = 0
        for t in trips_now:
            if t.seats.id == j:
                key = 1
        if key == 0:
            free_seats.append(j)



    for p in passengers:
        if p.id < min_id:
            min_id = p.id
        all_seats_val =[0 for j in range(max(all_seats))] + [0]
        for t in trips.filter(passenger=p, finished=True):
            if t.seats.id in free_seats:
                all_seats_val[t.seats.id] += 1

        string.append(all_seats_val)


    array = [[0 for j in range(len(all_seats_val))] for i in range(min_id)] + string[::-1]
    user_seats_matrix = np.array(array)

    return user_seats_matrix

def get_seat(id):
    return id

