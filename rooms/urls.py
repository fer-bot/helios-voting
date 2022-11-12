from django.urls import path

from . import views

urlpatterns = [
    path('', views.room_main,
         name='room_main'),
    path('create/', views.room_create,
         name='room_create'),
    path('update/<room_id>/', views.room_update_details,
         name='room_update_details'),
    path('open/<room_id>/', views.room_open,
         name='room_open'),
    path('close/<room_id>/', views.room_close,
         name='room_close'),
    path('release/<room_id>/', views.room_release,
         name='room_release'),
    path('update/<room_id>/authority/', views.room_update_authority,
         name='room_update_authority'),
    path('update/<room_id>/authority/<user_id>', views.room_delete_authority,
         name='room_delete_authority'),
    path('update/<room_id>/lock', views.room_update_lock,
         name='room_update_lock'),
    path('update/<room_id>/voter/', views.room_update_voter,
         name='room_update_voter'),
    path('update/<room_id>/voter/<user_id>', views.room_delete_voter,
         name='room_delete_voter'),
]
