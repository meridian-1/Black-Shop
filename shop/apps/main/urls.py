from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<slug:slug>/", views.clothing_item_detail, name="clothing_item_detail"),
]
