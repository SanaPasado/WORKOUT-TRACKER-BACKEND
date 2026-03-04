import logging
import os
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from dotenv import dotenv_values
from google import genai
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Exercise, UserProfile
from .models import WorkoutSplit
from .serializers import ExerciseSerializer, UserProfileSerializer, WorkoutSplitSerializer


logger = logging.getLogger(__name__)


@api_view(["GET"])
def getRoutes(request):
    routes = [
        "/auth/register/",
        "/users/login/",
        "/auth/token/refresh/",
        "/users/profile/",
        "/exercises/",
        "/chat/send-message/",
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
        password = attrs.get("password")

        user = None
        if identifier:
            if "@" in identifier:
                user = User.objects.filter(email__iexact=identifier).first()
            else:
                user = User.objects.filter(username=identifier).first()

        if not user:
            raise serializers.ValidationError(
                {"detail": "No account found with the provided credentials."}
            )

        if not password or not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "Incorrect password. Please try again."}
            )

        attrs["username"] = user.username

        data = super().validate(attrs)

        serializer = UserSerializer(self.user).data
        for k, v in serializer.items():
            data[k] = v

        profile = getattr(self.user, "profile", None)
        data["needs_profile"] = profile is None
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["POST"])
def forgot_password(request):
    email = (request.data.get("email") or "").strip().lower()
    if not email:
        return Response(
            {"detail": "Email is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response(
            {"detail": "No account is associated with this email address."},
            status=status.HTTP_404_NOT_FOUND,
        )

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    reset_token = default_token_generator.make_token(user)
    combined_token = f"{uidb64}:{reset_token}"
    frontend_reset_url = f"{settings.PASSWORD_RESET_FRONTEND_URL}?token={combined_token}"

    subject = "Reset your ANGRIT password"
    message = (
        "We received a request to reset your password.\n\n"
        f"Use this link to reset it:\n{frontend_reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    return Response(
        {"message": "Password reset email sent successfully."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def reset_password(request):
    token = (request.data.get("token") or "").strip()
    password = request.data.get("password")
    confirm_password = request.data.get("confirmPassword")

    if not token or not password or not confirm_password:
        return Response(
            {"detail": "token, password, and confirmPassword are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != confirm_password:
        return Response(
            {"detail": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        uidb64, raw_token = token.split(":", 1)
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (ValueError, TypeError, OverflowError, User.DoesNotExist):
        return Response(
            {"detail": "Invalid password reset token."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not default_token_generator.check_token(user, raw_token):
        return Response(
            {"detail": "This password reset link is invalid or has expired."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_password(password, user=user)
    except ValidationError as error:
        return Response(
            {"detail": error.messages},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(password)
    user.save()

    return Response(
        {"message": "Password has been reset successfully."},
        status=status.HTTP_200_OK,
    )


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


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def workout_split_list(request):
    if request.method == "GET":
        splits = WorkoutSplit.objects.filter(user=request.user).prefetch_related(
            "programs__exercise_items"
        )
        serializer = WorkoutSplitSerializer(splits, many=True)
        return Response(serializer.data)

    serializer = WorkoutSplitSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    split = serializer.save(user=request.user)
    response_serializer = WorkoutSplitSerializer(split)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def workout_split_detail(request, pk):
    split = get_object_or_404(
        WorkoutSplit.objects.prefetch_related("programs__exercise_items"),
        pk=pk,
        user=request.user,
    )

    if request.method == "GET":
        serializer = WorkoutSplitSerializer(split)
        return Response(serializer.data)

    if request.method == "PUT":
        serializer = WorkoutSplitSerializer(split, data=request.data)
        serializer.is_valid(raise_exception=True)
        split = serializer.save()
        return Response(WorkoutSplitSerializer(split).data)

    split.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

DEFAULT_MODEL_NAME = "gemini-2.5-flash"
TEMP_HARDCODED_GEMINI_API_KEY = "AIzaSyDUiSi3S1WMeBL5UtUt78QdcXp22t1fZ6M"

SYSTEM_PROMPT = """
You are Angrit AI Coach, a friendly expert fitness coach for our workout tracker app.

Rules:
- Keep responses practical, concise, and motivating.
- Focus on workouts, exercise form, programming splits, recovery, and basic nutrition habits.
- Personalize advice to beginner/intermediate users when details are limited.
- Prefer safe, progressive guidance (warm-up, proper form, manageable volume, rest days).
- Never claim medical expertise or diagnosis; for pain, injury, or health risk, advise seeing a licensed professional.
- If the request is unrelated to fitness/wellness/workout planning, reply exactly:
    "I'm sorry! I'm only able to help with fitness, workouts, recovery, and nutrition basics."
"""

@api_view(["POST"])
def chat_view(request):
  
    user_message = (request.data.get("message") or "").strip()
    if not user_message:
        return Response({"error": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    project_root = Path(__file__).resolve().parent.parent
    root_env = dotenv_values(project_root / ".env")
    base_env = dotenv_values(project_root / "base" / ".env")

    env_key = (os.environ.get("GEMINI_API_KEY") or "").strip()
    root_key = (root_env.get("GEMINI_API_KEY") or "").strip()
    base_key = (base_env.get("GEMINI_API_KEY") or "").strip()

    api_key = root_key or base_key or env_key
    if root_key:
        key_source = "project .env"
    elif base_key:
        key_source = "base/.env"
    elif env_key:
        key_source = "env"
    else:
        key_source = "missing"

    env_model = (os.environ.get("GEMINI_MODEL") or "").strip()
    root_model = (root_env.get("GEMINI_MODEL") or "").strip()
    base_model = (base_env.get("GEMINI_MODEL") or "").strip()
    model_name = root_model or base_model or env_model or DEFAULT_MODEL_NAME
    if root_model:
        model_source = "project .env"
    elif base_model:
        model_source = "base/.env"
    elif env_model:
        model_source = "env"
    else:
        model_source = "default"

    if not api_key:
        api_key = TEMP_HARDCODED_GEMINI_API_KEY.strip()
        key_source = "hardcoded fallback"

    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "(missing/invalid)"
    print(f"[chat_view] Gemini key source={key_source}, key={masked_key}, model source={model_source}, model={model_name}")

    # 3) Validate API key
    if not api_key:
        return Response(
            {"error": "Server misconfiguration: GEMINI_API_KEY is missing."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 4) Call Gemini
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}"

        result = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        reply_text = (getattr(result, "text", None) or "").strip()
        if not reply_text:
            return Response({"error": "Model returned an empty response."}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({"reply": reply_text}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("Gemini request failed")
        return Response({"error": f"Gemini request failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)