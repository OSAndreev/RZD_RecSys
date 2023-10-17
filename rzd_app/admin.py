from django.contrib import admin
from .models import *
# Register your models here.

class AdminPassenger(admin.ModelAdmin):
    list_display = ['id', 'last_name', 'first_name', 'patronymic', 'gender',  'about', 'contact', 'cluster', 'trip_with_child', 'trip_with_animals',
                    'regular_choice', 'smoking_attitude', 'having_children', 'sociability',
                    'pets_attitude', 'django_user']

class AdminTrip(admin.ModelAdmin):
    list_display = ['id', 'passenger', 'seats', 'finished', 'with_children', 'with_animals']


class AdminVan(admin.ModelAdmin):
    list_display = ['id', 'train', 'character']

class AdminSeat(admin.ModelAdmin):
    list_display = ['id', 'van', 'price', 'seat_number']

class AdminVanCharacter(admin.ModelAdmin):
    list_display = ['id', 'type', 'class_van', 'seat_quantity', 'food', 'info_entertaiment', 'linen', 'biotoilet',
                    'conditioner', 'cosmetic', 'press', 'pet', 'bath', 'business_lounge', 'taxi']

class AdminTrain(admin.ModelAdmin):
    list_display = ['id', 'name', 'place1', 'place2']

admin.site.register(Passenger, AdminPassenger)
admin.site.register(Trip, AdminTrip)
admin.site.register(Van, AdminVan)
admin.site.register(Seat, AdminSeat)
admin.site.register(VanCharacter, AdminVanCharacter)
admin.site.register(Train, AdminTrain)



