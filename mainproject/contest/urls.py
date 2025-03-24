from django.urls import path, include
from .import views

urlpatterns = [
    path('', views.index_view, name='index'),
     path('<int:id>/', views.contest_view, name='contest_view'),
]
