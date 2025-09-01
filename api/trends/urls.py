from django.urls import path
from . import views

urlpatterns = [
    path("latest-trends/", views.latest_trends, name="latest-trends"),
    path("scrape-save-trend/", views.scrape_save_trend, name="scrape-save-trend"),
]