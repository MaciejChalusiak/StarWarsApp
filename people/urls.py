from django.urls import path

from . import views

urlpatterns = [
    path("", views.people_home_page, name="people_home_page"),
    path("show_dataset/", views.show_dataset, name="show_dataset"),
    path("show_dataset/<int:data_set_id>/", views.show_dataset_details, name="show_dataset_details"),
    path("show_dataset/<int:data_set_id>/download/", views.download_dataset, name="download_dataset"),
    path("show_dataset/<int:data_set_id>/count/", views.count, name="count"),
    path("create_dataset/", views.create_dataset, name="create_dataset"),
]
