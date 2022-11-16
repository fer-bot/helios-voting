from django.urls import path

from . import views

urlpatterns = [
    path('', views.user_main, name='user_main'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('signup/', views.user_signup, name='user_signup'),
    path('hash/<hash_input>/', views.hash_input, name='hash_input'),
]
