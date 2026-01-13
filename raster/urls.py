from django.urls import path

from . import views

app_name = 'raster'

urlpatterns = [
    path('', views.index, name='index'),
]
