from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = DefaultRouter()
router.register("exercises", views.ExerciseViewSet, basename="exercise")

urlpatterns = [
    path('', views.getRoutes, name="routes"),
    path('auth/register/', views.register_user, name='register'),
    path('auth/verify-email/', views.verify_email, name='verify-email'),
    path('users/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/forgot-password/', views.forgot_password, name='forgot-password'),
    path('users/reset-password/', views.reset_password, name='reset-password'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/profile/', views.user_profile, name='user-profile'),
    path('premium/status/', views.premium_status, name='premium-status'),
    path('premium/paypal/create-subscription/', views.paypal_create_subscription, name='paypal-create-subscription'),
    path('premium/paypal/activate-subscription/', views.paypal_activate_subscription, name='paypal-activate-subscription'),
    path('premium/paypal/create-order/', views.paypal_create_subscription, name='paypal-create-order-legacy'),
    path('premium/paypal/capture-order/', views.paypal_activate_subscription, name='paypal-capture-order-legacy'),
    path('workouts/logs/', views.workout_log_list, name='workout-log-list'),
    path('workouts/logs/<int:pk>/', views.workout_log_detail, name='workout-log-detail'),
    path('workouts/dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    path('splits/', views.workout_split_list, name='workout-split-list'),
    path('splits/<int:pk>/', views.workout_split_detail, name='workout-split-detail'),
    path('chat/send-message/', views.chat_view, name='chat-view'),
    path('programs/generate/', views.generate_training_program, name='program-generate'),
]

urlpatterns += router.urls
