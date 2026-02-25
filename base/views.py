from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Exercise, UserProfile
from .serializers import ExerciseSerializer, UserProfileSerializer


@api_view(["GET"])
def getRoutes(request):
    routes = [
        "/auth/register/",
        "/users/login/",
        "/auth/token/refresh/",
        "/users/profile/",
        "/exercises/",
    ]
    return JsonResponse(routes, safe=False)


@api_view(["POST"])
def register_user(request):
    username_field = request.data.get("username")
    password_field = request.data.get("password")
    email_field = request.data.get("email")

    if not username_field or not password_field or not email_field:
        return Response(
            {"detail": "username, email, and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username_field).exists():
        return Response({"detail": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email_field).exists():
        return Response({"detail": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username_field,
        password=password_field,
        email=email_field,
    )
    UserProfile.objects.get_or_create(user=user)

    serializer = UserSerializerWithToken(user, many=False)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "_id", "name", "username", "email", "isAdmin"]

    def get__id(self, obj):
        return obj.id

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        name = obj.first_name
        if name == "":
            name = obj.email
        return name


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    needs_profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "_id", "username", "email", "name", "isAdmin", "token", "needs_profile"]

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

    def get_needs_profile(self, obj):
        profile = getattr(obj, "profile", None)
        return profile is None


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        identifier = attrs.get("username")
        if identifier and "@" in identifier:
            try:
                user = User.objects.get(email__iexact=identifier)
                attrs["username"] = user.username
            except User.DoesNotExist:
                pass

        data = super().validate(attrs)

        serializer = UserSerializer(self.user).data
        for k, v in serializer.items():
            data[k] = v

        profile = getattr(self.user, "profile", None)
        data["needs_profile"] = profile is None
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        serializer = UserProfileSerializer(profile, many=False)
        return Response(serializer.data)

    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exercise_list(request):
    qs = Exercise.objects.filter(is_active=True)

    q = request.query_params.get("q")
    if q:
        qs = qs.filter(name__icontains=q)

    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category__iexact=category)

    serializer = ExerciseSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def exercise_detail(request, pk):
    exercise = get_object_or_404(Exercise, pk=pk, is_active=True)
    serializer = ExerciseSerializer(exercise, many=False)
    return Response(serializer.data)
