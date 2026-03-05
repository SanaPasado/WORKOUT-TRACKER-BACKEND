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
    path('exercises/', views.ExerciseListView.as_view(), name='exercise-list'),
    path('exercises/create/', views.ExerciseCreateView.as_view(), name='exercise-create'),
    path('exercises/<int:pk>/', views.ExerciseDetailView.as_view(), name='exercise-detail'),
    path('exercises/<int:pk>/update/', views.ExerciseUpdateView.as_view(), name='exercise-update'),
    path('exercises/<int:pk>/delete/', views.ExerciseDeleteView.as_view(), name='exercise-delete'),
    path('chat/send-message/', views.chat_view, name='chat-view'),
]