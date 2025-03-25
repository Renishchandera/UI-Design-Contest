from django.urls import path, include
from .import views
urlpatterns = [
    path('', views.index_view, name='index_view'),
     path('<int:contest_id>/', views.contest_view, name='contest_view'),
     path('contest/<int:contest_id>/participate/', views.participate, name='participate'),
]
