from .views import *

import random
from .models import*

def fill_passengers_seats(train):
    vans = Van.objects.filter(train=train)
    trips = Trip.objects.filter(finished=False)

    for van in vans:
        for seat in Seat.objects.filter(van=van):
            for t in trips:
                if t.seats == seat:
                    break
            else:
                if random.randint(1,5) <= 3:
                    new_user = User.objects.create(username=(str(train.name)+str(van.id)+str(seat.seat_number)+str(random.randint(1,100))), password=0)
                    new_user.save()
                    new_pass = Passenger.objects.create(last_name=(str(train.name)+str(van.id)+str(seat.seat_number)),
                                                        first_name=str(train.name)+str(van.id)+str(seat.seat_number),
                                                        patronymic='',
                                                        django_user=new_user,
                                                        gender=random.choice([True,False]),
                                                        age=random.randint(18,60),
                                                        about= '',
                                                        contact='0',
                                                        cluster=1,
                                                        trip_with_child=random.randint(0,5),
                                                        trip_with_animals= random.choice([True,False]),

                                                        regular_choice = random.randint(1,4),
                                                        smoking_attitude = random.randint(1,5),
                                                        having_children = random.randint(0,1),
                                                        sociability = random.randint(1,5),
                                                        pets_attitude= random.randint(0,1))
                    new_pass.cluster = get_cluster(new_pass.age, new_pass.smoking_attitude, new_pass.sociability, new_pass.gender)
                    new_pass.save()

                    new_trip = Trip.objects.create(passenger=new_pass, seats=seat, finished=False,
                                                   with_children=new_pass.trip_with_child,
                                                   with_animals=new_pass.trip_with_animals)
                    new_trip.save()



