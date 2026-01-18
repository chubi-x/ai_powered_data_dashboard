from django.urls import path

from . import views

app_name = 'raster'

urlpatterns = [
    path('', views.index, name='index'),
    path('viewer/', views.ViewerProxyView.as_view(), name='viewer_proxy'),
    path('tiles/<int:z>/<int:x>/<int:y>/', views.TileProxyView.as_view(), name='tile_proxy'),
]
