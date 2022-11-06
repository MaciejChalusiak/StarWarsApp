from django.urls import path

from . import views

urlpatterns = [
    path('show_dataset/', views.show_dataset, name='show_dataset'),
    path('show_dataset/<int:data_set_id>/', views.show_dataset_details, name='show_dataset_details'),
    path('create_dataset', views.create_dataset, name='create_dataset'),
]
