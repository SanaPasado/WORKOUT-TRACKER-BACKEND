from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('', views.getRoutes, name="routes"),
    path('auth/register/', views.register_user, name='register'),
    path('users/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/forgot-password/', views.forgot_password, name='forgot-password'),
    path('users/reset-password/', views.reset_password, name='reset-password'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/profile/', views.user_profile, name='user-profile'),
    path('exercises/', views.exercise_list, name='exercise-list'),
    path('exercises/<int:pk>/', views.exercise_detail, name='exercise-detail'),
    path('splits/', views.workout_split_list, name='workout-split-list'),
    path('splits/<int:pk>/', views.workout_split_detail, name='workout-split-detail'),
    path('chat/send-message/', views.chat_view, name='chat-view'),
]