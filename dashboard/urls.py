from django.urls import path

from . import views
from . import api_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    
    # API endpoints
    path('api/regions/', api_views.regions_list, name='api_regions'),
    path('api/modules/', api_views.modules_list, name='api_modules'),
    path('api/projections/', api_views.projections_list, name='api_projections'),
]
