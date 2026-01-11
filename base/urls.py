from django.urls import path
from . import views

urlpatterns = [
    path('routes/', views.getRoutes, name="routes"),
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login_user, name='login'),
]