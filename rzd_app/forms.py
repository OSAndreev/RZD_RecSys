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

        widgets = {
            "last_name": TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Фамилия'
            }),
            "first_name": TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Имя'
            }),
            "patronymic": TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Отчество'
            }),
            "age": NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Возраст'
            }),

            "about": TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Подробнее о вас'
            }),

            "contact": TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Контакт для связи'
            }),

            "regular_choice": Select(
                attrs={
                    'class': 'form-control form-control-lg',
                }),

            "smoking_attitude": Select(
                attrs={
                    'class': 'form-control form-control-lg',
                }),

            "having_children": Select(
                attrs={
                    'class': 'form-control form-control-lg',
                }),

            "sociability": Select(
                attrs={
                    'class': 'form-control form-control-lg',
                }),

            "pets_attitude": Select(
                attrs={
                    'class': 'form-control form-control-lg',
                }),
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

        widgets = {

            "trip_with_child": Select(attrs={
                'class': 'form-control form-control-sm'
            }),

        }



