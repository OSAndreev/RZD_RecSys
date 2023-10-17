from django.forms import ModelForm, TextInput, DateInput, NumberInput, Select, EmailInput, HiddenInput
from .models import *
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class RegisterUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class PassengerForm(ModelForm):
    class Meta:
        model = Passenger
        fields = ['last_name', 'first_name', 'patronymic', 'age', 'about', 'contact', 'regular_choice',
                  'smoking_attitude', 'having_children', 'sociability', 'pets_attitude']
        labels = {
            "last_name": "Фамилия",
            "first_name": "Имя",
            "patronymic": "Отчество",
            "age": "Возраст",
            "about": "О себе",
            "contact": "Телефон",
            "regular_choice": "Чаще всего предпочитаете",
            "smoking_attitude": "Ваше отношение к курящим попутчикам",
            "having_children": "Планируете ли вы путешествовать с ребенком",
            "sociability": "Оцените, насколько Вы общительны в поездке",
            "pets_attitude": "Ваше отношение к попутчикам с домашними животными",


        }

class AuthUserForm(AuthenticationForm, forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')
        labels = {'username': 'Имя пользователя',
                  'password': 'Пароль'}


class ChildrenAnimalsForm(ModelForm):
    class Meta:
        model = Passenger
        fields = ['trip_with_child', 'trip_with_animals']
        labels = {
            'trip_with_child': 'Детей в поездке:',
            'trip_with_animals': 'Еду с животным',
        }


