# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from app import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    # The backtest page
    path('dashboard.html', views.dashboard, name='dashboard'),

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
