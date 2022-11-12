from django.urls import path

from . import views

urlpatterns = [
    path('', views.authorithy_main, name='authority_main'),
    path('<room_id>/', views.authority_submit, name='authority_submit'),
]
