"""rzd_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, re_path
from rzd_app.views import *
from rzd_app import views

def redirect_page(request, pk=''):
    return redirect('main_page')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', start_page, name='start_page'),
    path('login/', LoginUserView.as_view(), name='login_page'),
    path('register/', RegisterUserView.as_view(), name='register_page'),
    path('main_page/', main_page, name='main_page'),
    path('register/create_user', create_user, name='create_user'),
    path('main_page/routes/<int:pk>', route_page, name='route_page'),
    path('main_page/routes/', redirect_page),
    path('main_page/<int:pk>', redirect_page),
    path('main_page/routes/chosen/<int:pk>', van_page, name='van_page'),
    path('main_page/routes/chosen/<int:tr>/<int:vn>/<int:st>/buy', buy_ticket, name='buy_ticket'),
    path('main_page/routes/chosen/<int:tr>/<int:vn>/<int:st>/reject', reject_ticket, name='reject_ticket'),
    path('main_page/my_trips', my_trips, name='my_trips'),
    path('main_page/my_trips/<int:id>/reject', reject_ticket)


]
