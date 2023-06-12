from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("register/", views.registerPage, name="register"),
    path("logout/", views.logoutUser, name="logout"),
    path("", views.home, name="home"),
    path("profile/<str:pk>", views.userProfile, name="profile"),
    path("topics", views.browseTopics, name="topics"),
    path("room", views.room, name="room"),
    path("room/<str:pk>/", views.room, name="room"),
    path("room/create", views.createRoom, name="create-room"),
    path("room/update/<str:pk>", views.updateRoom, name="update-room"),
    path("room/delete/<str:pk>", views.deleteRoom, name="delete-room"),
    path("room/messages/delete/<str:pk>", views.deleteMessage, name="delete-message"),
    path("update-user", views.updateUser, name="update-user"),
]
