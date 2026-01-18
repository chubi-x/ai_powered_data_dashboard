from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("charts/", views.GetChartsView.as_view(), name="get_charts"),
    path("charts/timeseries", views.timeseries_chart, name="get_timeseries_chart"),
    path("charts/pie", views.pie_chart, name="get_pie_chart"),
]
