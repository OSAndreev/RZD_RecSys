from django.db import models
from django.contrib.auth.models import User
class Passenger(models.Model):
    django_user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    patronymic = models.CharField(max_length=30, null=True, blank=True) #отчество
    gender = models.BooleanField(default=True,
                                 choices=[(True, 'Мужской'), (False, 'Женский')])
    age = models.IntegerField()
    about = models.CharField(max_length=250)
    contact = models.CharField(max_length=40)
    cluster = models.IntegerField(null=True,blank=True)
    trip_with_child = models.IntegerField(choices=[
        (0, "Еду один"),
        (1, "Один ребенок"),
        (2, "Двое детей"),
        (3, "Трое детей"),
        (4, "Четверо детей"),
        (5, "Пятеро детей")

    ], default=0)
    trip_with_animals = models.BooleanField(default=False)

    #Фичи
    regular_choice = models.IntegerField(choices=[
        #(0, 'Покупаю билет впервые'),
        (1, 'Плацкарт'),
        (2, 'Купе'),
        (3, 'СВ'),
        (4, 'Люкс')
    ])

    smoking_attitude = models.IntegerField(choices=[(1, 'Крайне негативно'),
                                                    (2, 'Негативно'),
                                                    (3, 'Нейтрально'),
                                                    (4, 'Положительно'),
                                                    (5, 'Крайне положительно')])

    having_children = models.IntegerField(choices=[
        (1, 'Да'),
        (0, 'Нет')
    ])
    sociability = models.IntegerField(choices=[(1, 'Предпочитаю не общаться в поездке'),
                                               (2, 'Редко общаюсь'),
                                               (3, 'По-настроению'),
                                               (4, 'Часто общаюсь'),
                                               (5, 'Люблю заводить новые знакомства в поездах')])

    pets_attitude = models.IntegerField(choices=[
        (1, 'Положительно'),
        (0, 'Отрицательно')
    ])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}, {self.patronymic}, {self.gender}, {self.age}, {self.about}, {self.contact},' \
               f'{self.cluster}, {self.trip_with_child}, {self.trip_with_animals},'\
               f'{self.regular_choice}, {self.smoking_attitude}, {self.having_children}, {self.sociability},' \
               f'{self.pets_attitude}, {self.django_user}'

class VanCharacter(models.Model):
    type = models.IntegerField(choices=[
        (1, 'Плацкарт'),
        (2, 'Купе'),
        (3, 'СВ'),
        (4, 'Люкс')
    ])

    class_van = models.IntegerField(choices=[
        (1, '3Б'),
        (2, '3Э'),
        (3, '2Т'),
        (4, '2Э'),
        (5, '1Э'),
        (6, '1Т'),
        (7, '1М')
    ])

    seat_quantity = models.IntegerField()

    food = models.BooleanField()
    info_entertaiment = models.BooleanField()
    linen = models.BooleanField()
    biotoilet = models.BooleanField()
    conditioner = models.BooleanField()
    cosmetic = models.BooleanField()
    press = models.BooleanField()
    pet = models.BooleanField()
    bath = models.BooleanField()
    business_lounge = models.BooleanField()
    taxi = models.BooleanField()

    def __str__(self):
        return f'{self.type}, {self.class_van}, {self.seat_quantity}, {self.food}, {self.info_entertaiment}, {self.linen},' \
               f'{self.biotoilet}, {self.conditioner}, {self.cosmetic}, {self.press},' \
               f'{self.pet}, {self.bath}, {self.business_lounge}, {self.taxi} '

class Train(models.Model):
    name = models.CharField(max_length=30)
    place1 = models.CharField(max_length=30)
    place2 = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name}, {self.place1}, {self.place2}'


class Van(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    character = models.ForeignKey(VanCharacter, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.train}, {self.character}'


class Seat(models.Model):
    van = models.ForeignKey(Van, on_delete=models.CASCADE)
    price = models.IntegerField(null=True)
    seat_number = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.van}, {self.price}, {self.seat_number}'


class Trip(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    seats = models.ForeignKey(Seat, on_delete=models.CASCADE)
    finished = models.BooleanField(default=False)
    with_children = models.IntegerField(default=0)
    with_animals = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.passenger}, {self.seats}, {self.finished}, {self.with_children}, {self.with_animals}'

