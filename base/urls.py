from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('room/<str:pk>',views.room,name='room'),
    path('user-profile/<str:pk>',views.userProfile,name='user-profile'),

    path('login-user/', views.loginUser, name='login-user'),
    path('logout-user/', views.logoutUser, name='logout-user'),
    path('register-user/', views.registerUser, name='register-user'),
    path('update-user/', views.updateUser, name='update-user'),

    path('create-room/',views.createRoom,name='create-room'),
    path('update-room/<str:pk>',views.updateRoom,name='update-room'),
    path('update-message/<str:pk>',views.updateMessage,name='update-message'),
    path('delete-room/<str:pk>',views.deleteRoom,name='delete-room'),    
    path('delete-message/<str:pk>',views.deleteMessage,name='delete-message'),

    path('topic-page/',views.topicPage,name='topic-page'),
    path('activity-page/',views.activityPage,name='activity-page'),
]
