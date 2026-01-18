from django.urls import path

from . import views

app_name = "raster"

urlpatterns = [
    path("tiles/<int:z>/<int:x>/<int:y>@1x", views.get_tiles, name="tile_proxy"),
    path("info/", views.get_info, name="info_proxy"),
    path("json/", views.get_tile_json, name="tiles_json_proxy"),
]
