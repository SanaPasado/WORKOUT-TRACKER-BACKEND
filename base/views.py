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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
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

from serializers import ExerciseSerializer
from rest_framework.generics import ListAPIView
from models import Exercise

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exercise_list(request):
    qs = Exercise.objects.all()

    q = request.query_params.get("q")
    if q:
        qs = qs.filter(name__icontains=q)  # replace "name" if your field is different

    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category__name__icontains=category).distinct()  # adjust to your model relation

    serializer = ExerciseSerializer(qs, many=True)
    return Response(serializer.data)