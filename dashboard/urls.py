from django.urls import path

from . import views
from . import api_views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/charts/", views.GetChartsView.as_view(), name="get_charts"),
    path("api/charts/timeseries", views.timeseries_chart, name="get_timeseries_chart"),
    path("api/charts/pie", views.pie_chart, name="get_pie_chart"),
    path("api/projections/", api_views.projections_list, name="api_projections"),
]
