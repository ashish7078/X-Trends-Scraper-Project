from django.urls import path
from . import views

urlpatterns = [
    path("latest-trends/", views.latest_trends, name="latest-trends"),
    path("trigger-scrape/", views.trigger_scrape, name="trigger-scrape"),
]