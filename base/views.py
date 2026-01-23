from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

@api_view(['GET'])

def getRoutes(request):
    routes = [
        '/api/token/',
        '/api/token/refresh/',

        '/api/users/login/',
        '/api/users/register/',
        '/api/users/profile/',
        
        

    ]
    return JsonResponse(routes, safe=False)


# @api_view(['POST'])
# def register(request):
#     email = request.data.get('email')
#     password = request.data.get('password')
    
#     if not email or not password:
#         return Response({'error': 'Email and password are required'}, status=400)
    
#     if User.objects.filter(email=email).exists():
#         return Response({'error': 'Email already exists'}, status=400)
    
#     user = User.objects.create_user(username=email, email=email, password=password)
    
#     # Generate JWT tokens for the new user
#     refresh = RefreshToken.for_user(user)
    
#     return Response({
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#         'user': {
#             'id': user.id,
#             'email': user.email
#         }
#     }, status=201)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_user(request):
    print(request.data['username'])
    username_field = request.data['username']
    password_field = request.data['password']
    email_field = request.data['email'] 

    User.objects.create_user(username=username_field, password=make_password(password_field), email=email_field)
    return Response ({'detail', request.data})
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        serializer = UserSerializer(self.user).data 
       
        for k, v in serializer.items():
            data[k] = v
        
        return data
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
   
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many = False)
    return Response(serializer.data)

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', '_id', 'name', 'username', 'email', 'isAdmin']
    
    def get__id(self, obj):
        return obj.id
    
    def get_isAdmin(self, obj):
        return obj.is_staff
    
    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin', 'token']
    
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

