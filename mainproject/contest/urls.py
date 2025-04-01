from django.urls import path, include
from .import views
urlpatterns = [
    path('', views.index_view, name='index_view'),
     path('<int:contest_id>/', views.contest_view, name='contest_view'),
     path('contest/<int:contest_id>/participate/', views.participate, name='participate'),
     path('profile/<int:user_id>', views.profile_view, name="profile_view"),
    path('edit-profile/', views.edit_profile_view, name='edit_profile_view'),
     path('show_voting_view', views.show_voting_view,name="show_voting_view"),
     path('mycontests', views.mycontests_view, name="mycontests_view"),
     path('<int:contest_id>/voting', views.voting_view, name="voting_view"),
     path("vote/<int:submission_id>/", views.vote_submission, name="vote_submission"),
      path('claim_reward/<int:submission_id>/', views.claim_reward, name='claim_reward'),
]
