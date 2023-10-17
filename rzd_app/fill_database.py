from .models import *

def fill_database_van_character():
    character = list(obj for obj in VanCharacter.objects.values_list('id'))
    if character == []:
        ch = VanCharacter.objects.create(type=1, class_van=1, seat_quantity=54, food=False, info_entertaiment=False, linen=False, biotoilet=True, conditioner=True, cosmetic=False, press=False, pet=True, bath=False, business_lounge=False, taxi=False)
        ch.save()
        ch = VanCharacter.objects.create(type=1, class_van=2, seat_quantity=54, food=False, info_entertaiment=False,
                                         linen=False, biotoilet=True, conditioner=True, cosmetic=False, press=False,
                                         pet=False, bath=False, business_lounge=False, taxi=False)
        ch.save()
        ch = VanCharacter.objects.create(type=2, class_van=3, seat_quantity=36, food=True, info_entertaiment=True,
                                         linen=True, biotoilet=True, conditioner=True, cosmetic=True, press=True,
                                         pet=False, bath=False, business_lounge=False, taxi=False)
        ch.save()
        ch = VanCharacter.objects.create(type=2, class_van=4, seat_quantity=36, food=True, info_entertaiment=True,
                                         linen=True, biotoilet=True, conditioner=True, cosmetic=True, press=True,
                                         pet=True, bath=False, business_lounge=False, taxi=False)
        ch.save()
        ch = VanCharacter.objects.create(type=3, class_van=5, seat_quantity=18, food=True, info_entertaiment=True,
                                         linen=True, biotoilet=True, conditioner=True, cosmetic=True, press=True,
                                         pet=True, bath=True, business_lounge=True, taxi=False)
        ch.save()
        ch = VanCharacter.objects.create(type=3, class_van=6, seat_quantity=18, food=True, info_entertaiment=True,
                                         linen=True, biotoilet=True, conditioner=True, cosmetic=True, press=True,
                                         pet=False, bath=True, business_lounge=True, taxi=False)
        ch.save()
        ch = VanCharacter.objects.create(type=4, class_van=7, seat_quantity=12, food=True, info_entertaiment=True,
                                         linen=True, biotoilet=True, conditioner=True, cosmetic=True, press=True,
                                         pet=True, bath=True, business_lounge=True, taxi=True)
        ch.save()



def fill_database_train():
    train = list(obj for obj in Train.objects.values_list('id'))
    if train == []:
        tr = Train.objects.create(name="Волга", place1="Нижний-Новгород", place2="Санкт-Петербург")
        tr.save()
        tr = Train.objects.create(name="Арктика", place1="Москва", place2="Мурманск")
        tr.save()
        tr = Train.objects.create(name="Премиум", place1="Москва", place2="Казань")
        tr.save()


def fill_database_van():
    van = list(obj for obj in Van.objects.values_list('id'))
    if not van:
        sp = ["Волга", "Арктика", "Премиум"]
        dict = {"Волга": [1, 3, 4, 5,],
                "Арктика": [1, 2, 3, 4, 5],
                "Премиум": [3, 4, 5, 6, 7]}
        for elem in sp:
            for x in dict[elem]:
                train = Train.objects.filter(name=elem).first()
                van_character = VanCharacter.objects.filter(class_van=x).first()
                if train and van_character:
                    v = Van.objects.create(train=train, character=van_character)
                    v.save()

