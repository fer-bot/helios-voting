from django.urls import path

from . import views

urlpatterns = [
    path('', views.voter_main, name='voter_main'),
    path('<room_id>/', views.voter_choice, name='voter_choice'),
    path('<room_id>/result', views.voter_voting_result,
         name='voter_voting_result'),
    path('<room_id>/vote/', views.voter_vote, name='voter_vote'),
    path('<room_id>/voters/', views.voter_view_voters, name='voter_view_voters'),
    path('<room_id>/authorities/', views.voter_view_authorities,
         name='voter_view_authorities'),
]
