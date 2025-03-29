from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/chat/', views.chat_response, name='chat_response')
]