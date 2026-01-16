from django.urls import path
from .views import MyTokenObtainPairView, getRoutes

urlpatterns = [
    path('routes/', getRoutes, name="routes"),
    # path('auth/register/', register, name='register'),
    # path('auth/login/', login_user, name='login'),
    path('user/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
]