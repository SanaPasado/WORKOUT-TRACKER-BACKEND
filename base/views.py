from importlib.resources import path
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

@api_view(['GET'])

def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/token/refresh/',

        '/api/users/login/',
        '/api/users/register/',
        '/api/users/profile/',
        
        

    ]
    return JsonResponse('Hello', safe=False)


@api_view(['POST'])
def register(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if User.objects.filter(email=email).exists():
        return Response({'email': 'Email already exists'}, status=400)
    
    user = User.objects.create_user(username=email, email=email, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    
    return Response({'token': token.key, 'user': {'email': user.email}})

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    user = User.objects.filter(email=email).first()
    if user and user.check_password(password):
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': {'email': user.email}})
    
    return Response({'error': 'Invalid credentials'}, status=401)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        # Add custom claims
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        data['email'] = self.user.email
        # ...

        return data
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
