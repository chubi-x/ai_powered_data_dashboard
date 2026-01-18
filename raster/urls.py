from django.urls import path

from . import views

app_name = "raster"

urlpatterns = [
    path("tiles/<int:z>/<int:x>/<int:y>/", views.TileProxyView.as_view(), name="tile_proxy"),
    path("info/", views.InfoProxyView.as_view(), name="info_proxy"),
]
