from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('disputes/', views.DisputeListView.as_view(), name='dispute_list'),
    path('disputes/partial/', views.dispute_list_partial, name='dispute_list_partial'),
    path('disputes/create/', views.dispute_create, name='dispute_create'),
    path('disputes/create/form/', views.dispute_create_form, name='dispute_create_form'),
    path('disputes/<int:pk>/', views.DisputeDetailView.as_view(), name='dispute_detail'),
    # path('', views.dispute_list, name='dispute_list'),
    # path('add-dispute/', views.add_dispute_modal, name='add_dispute_modal'),
]
