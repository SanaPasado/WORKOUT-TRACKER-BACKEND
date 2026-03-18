import logging
import os
import json
import re
from smtplib import SMTPException
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from dotenv import dotenv_values
from google import genai
from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from requests.auth import HTTPBasicAuth

from .models import (
    ChatConversation,
    ChatMessage,
    Exercise,
    UserProfile,
    WorkoutLog,
    WorkoutSplit,
    WorkoutProgram,
    WorkoutProgramExercise,
)
from .permissions import IsPremiumUserOrAdmin
from .serializers import (
    ChatConversationSerializer,
    ChatMessageSerializer,
    ExerciseDetailSerializer,
    ExerciseListSerializer,
    ExerciseWriteSerializer,
    UserProfileSerializer,
    WorkoutLogSerializer,
    WorkoutSplitSerializer,
)


logger = logging.getLogger(__name__)

FREE_CHAT_MESSAGE_LIMIT = 5
CHAT_HISTORY_CONTEXT_LIMIT = 20
CHAT_HISTORY_RESPONSE_LIMIT = 200


def is_profile_complete(profile):
    if not profile:
        return False
    required_fields = [
        profile.age,
        profile.height_cm,
        profile.weight_kg,
    ]
    return all(value is not None for value in required_fields)


@api_view(["GET"])
def getRoutes(request):
    routes = [
        "/auth/register/",
        "/auth/verify-email/",
        "/users/login/",
        "/users/forgot-password/",
        "/users/reset-password/",
        "/auth/token/refresh/",
        "/users/profile/",
        "/premium/status/",
        "/premium/paypal/create-order/",
        "/premium/paypal/capture-order/",
        "/exercises/",
        "/exercises/{id}/",
        "/chat/history/",
        "/chat/send-message/",
        "/programs/generate/",
    ]
    return JsonResponse(routes, safe=False)


class ExerciseListCreateView(generics.ListCreateAPIView):
    queryset = Exercise.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ExerciseWriteSerializer
        return ExerciseListSerializer

    def get_queryset(self):
        queryset = Exercise.objects.all().order_by("exercise_name", "id")

        search_term = (self.request.query_params.get("q") or "").strip()
        if search_term:
            queryset = queryset.filter(
                Q(exercise_name__icontains=search_term)
                | Q(description__icontains=search_term)
                | Q(muscle_groups_targeted__icontains=search_term)
            )

        category = (self.request.query_params.get("category") or "").strip().lower()
        if category:
            queryset = queryset.filter(category=category)

        difficulty_level = (self.request.query_params.get("difficulty_level") or "").strip().lower()
        if difficulty_level:
            queryset = queryset.filter(difficulty_level=difficulty_level)

        return queryset


class ExerciseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exercise.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAuthenticated(), IsPremiumUserOrAdmin()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ExerciseDetailSerializer
        return ExerciseWriteSerializer


def _get_paypal_base_url():
    mode = (settings.PAYPAL_MODE or "sandbox").strip().lower()
    if mode == "live":
        return "https://api-m.paypal.com"
    return "https://api-m.sandbox.paypal.com"


def _get_paypal_checkout_base_url():
    mode = (settings.PAYPAL_MODE or "sandbox").strip().lower()
    if mode == "live":
        return "https://www.paypal.com/checkoutnow"
    return "https://www.sandbox.paypal.com/checkoutnow"


def _get_paypal_access_token():
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        raise ValueError("PayPal credentials are not configured.")

    response = requests.post(
        f"{_get_paypal_base_url()}/v1/oauth2/token",
        data={"grant_type": "client_credentials"},
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        auth=HTTPBasicAuth(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
        timeout=20,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"PayPal token request failed: {response.text[:300]}")

    access_token = response.json().get("access_token")
    if not access_token:
        raise RuntimeError("PayPal token response missing access_token.")
    return access_token


def _paypal_request(method, path, access_token, payload=None):
    response = requests.request(
        method,
        f"{_get_paypal_base_url()}{path}",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
        json=payload,
        timeout=20,
    )

    if response.status_code >= 400:
        raise RuntimeError(f"PayPal API request failed: {response.text[:300]}")

    return response.json()


@api_view(["POST"])
def register_user(request):
    username_field = (request.data.get("username") or "").strip()
    password_field = request.data.get("password")
    email_field = (request.data.get("email") or "").strip().lower()

    if not username_field or not password_field or not email_field:
        return Response(
            {"detail": "username, email, and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if User.objects.filter(username=username_field).exists():
        return Response({"detail": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email_field).exists():
        return Response({"detail": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password_field)
    except ValidationError as error:
        return Response(
            {"detail": error.messages},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=username_field,
                password=password_field,
                email=email_field,
                is_active=False,
            )
            UserProfile.objects.get_or_create(user=user)

            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            verify_token = default_token_generator.make_token(user)
            combined_token = f"{uidb64}:{verify_token}"
            verify_url = f"{settings.EMAIL_VERIFICATION_FRONTEND_URL}?token={combined_token}"

            send_mail(
                "Verify your ANGRIT account",
                (
                    "Welcome to ANGRIT. Please verify your email address before signing in.\n\n"
                    f"Verification link:\n{verify_url}\n\n"
                    "If you did not create this account, you can ignore this email."
                ),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
    except SMTPException:
        logger.exception("SMTP failed while sending verification email")
        return Response(
            {"detail": "Unable to send verification email. Please verify SMTP configuration."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception:
        logger.exception("Unexpected error while registering user")
        return Response(
            {"detail": "Registration failed. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "message": "Account created. Please check your email and verify your account before login.",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "POST"])
def verify_email(request):
    raw_token = ""
    if request.method == "GET":
        raw_token = (request.query_params.get("token") or "").strip()
    else:
        raw_token = (request.data.get("token") or "").strip()

    if not raw_token:
        return Response(
            {"detail": "Verification token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        uidb64, token = raw_token.split(":", 1)
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (ValueError, TypeError, OverflowError, User.DoesNotExist):
        return Response(
            {"detail": "Invalid verification token."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not default_token_generator.check_token(user, token):
        return Response(
            {"detail": "This verification link is invalid or has expired."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user.is_active:
        return Response(
            {"message": "Email is already verified. You can log in now."},
            status=status.HTTP_200_OK,
        )

    user.is_active = True
    user.save(update_fields=["is_active"])

    return Response(
        {"message": "Email verified successfully. You can now log in."},
        status=status.HTTP_200_OK,
    )


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
        return not is_profile_complete(profile)


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

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "Please verify your email before logging in."}
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

        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        data["needs_profile"] = not is_profile_complete(profile)
        data["is_premium"] = profile.is_premium
        data["remaining_free_messages"] = (
            None
            if profile.is_premium
            else max(0, FREE_CHAT_MESSAGE_LIMIT - int(profile.free_chat_messages_used or 0))
        )
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

    if not user.is_active:
        return Response(
            {"detail": "This account is not verified yet. Please verify your email first."},
            status=status.HTTP_403_FORBIDDEN,
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

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except SMTPException:
        logger.exception("SMTP failed while sending password reset email")
        return Response(
            {"detail": "Unable to send reset email. Please verify SMTP configuration."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception:
        logger.exception("Unexpected error while sending password reset email")
        return Response(
            {"detail": "Unable to send reset email right now. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def premium_status(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return Response(
        {
            "is_premium": profile.is_premium,
            "premium_provider": profile.premium_provider,
            "premium_order_id": profile.premium_order_id,
            "premium_since": profile.premium_since,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def paypal_create_subscription(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.is_premium:
        return Response(
            {"detail": "You already have premium access."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        if not settings.PAYPAL_PLAN_ID:
            return Response(
                {"detail": "PayPal plan ID is not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        access_token = _get_paypal_access_token()
        subscription_payload = {
            "plan_id": settings.PAYPAL_PLAN_ID,
            "custom_id": str(request.user.id),
            "application_context": {
                "brand_name": "ANGRIT",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "return_url": settings.PAYPAL_RETURN_URL,
                "cancel_url": settings.PAYPAL_CANCEL_URL,
            },
        }

        subscription_response = _paypal_request(
            "POST",
            "/v1/billing/subscriptions",
            access_token,
            payload=subscription_payload,
        )

        approval_url = None
        for link in subscription_response.get("links", []):
            rel = (link.get("rel") or "").strip().lower()
            if rel in {"approve", "payer-action"}:
                approval_url = link.get("href")
                break

        if not approval_url and subscription_response.get("id"):
            approval_url = f"{_get_paypal_checkout_base_url()}?token={subscription_response.get('id')}"

        if not approval_url:
            return Response(
                {"detail": "Unable to create PayPal approval URL."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "subscriptionID": subscription_response.get("id"),
                "approve_url": approval_url,
            },
            status=status.HTTP_201_CREATED,
        )
    except ValueError as error:
        return Response({"detail": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.RequestException:
        logger.exception("Network error while creating PayPal subscription")
        return Response(
            {"detail": "Unable to reach PayPal. Please try again later."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except RuntimeError as error:
        logger.exception("PayPal subscription creation failed")
        return Response({"detail": str(error)}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def paypal_activate_subscription(request):
    subscription_id = (
        request.data.get("subscriptionID")
        or request.data.get("token")
        or request.data.get("orderID")
        or ""
    ).strip()
    if not subscription_id:
        return Response(
            {"detail": "subscriptionID is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if profile.is_premium and profile.premium_order_id == subscription_id:
        return Response(
            {"message": "Premium already activated.", "is_premium": True},
            status=status.HTTP_200_OK,
        )

    try:
        access_token = _get_paypal_access_token()
        subscription_details = _paypal_request(
            "GET",
            f"/v1/billing/subscriptions/{subscription_id}",
            access_token,
        )

        subscription_status = (subscription_details.get("status") or "").upper()
        if subscription_status not in {"ACTIVE", "APPROVED"}:
            if subscription_status == "APPROVAL_PENDING":
                return Response(
                    {"detail": "Subscription is pending approval. Please complete PayPal approval and retry."},
                    status=status.HTTP_202_ACCEPTED,
                )

            return Response(
                {"detail": f"Subscription status is {subscription_status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile.is_premium = True
        profile.premium_provider = "paypal_subscription"
        profile.premium_order_id = subscription_id
        profile.premium_since = timezone.now()
        profile.save(update_fields=["is_premium", "premium_provider", "premium_order_id", "premium_since"])

        return Response(
            {
                "message": "Premium subscription activated successfully.",
                "is_premium": True,
                "subscription_status": subscription_status,
            },
            status=status.HTTP_200_OK,
        )
    except ValueError as error:
        return Response({"detail": str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except requests.RequestException:
        logger.exception("Network error while activating PayPal subscription")
        return Response(
            {"detail": "Unable to reach PayPal. Please try again later."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except RuntimeError as error:
        logger.exception("PayPal subscription activation failed")
        return Response({"detail": str(error)}, status=status.HTTP_502_BAD_GATEWAY)


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


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def workout_log_list(request):
    if request.method == "GET":
        logs = WorkoutLog.objects.filter(user=request.user)
        serializer = WorkoutLogSerializer(logs, many=True)
        return Response(serializer.data)

    serializer = WorkoutLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    log = serializer.save(user=request.user)
    return Response(WorkoutLogSerializer(log).data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def workout_log_detail(request, pk):
    log = get_object_or_404(WorkoutLog, pk=pk, user=request.user)
    log.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    logs = WorkoutLog.objects.filter(user=request.user)
    workout_dates = sorted({log.date for log in logs}, reverse=True)

    today = timezone.now().date()
    date_set = set(workout_dates)

    current_streak = 0
    cursor_date = today
    while cursor_date in date_set:
        current_streak += 1
        cursor_date -= timedelta(days=1)

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    weekly_days_completed = sorted(
        [day.isoformat() for day in workout_dates if week_start <= day <= week_end]
    )

    total_minutes = sum(max(1, int(log.sets) * 2) for log in logs)

    return Response(
        {
            "total_workouts": len(workout_dates),
            "total_minutes": total_minutes,
            "current_streak": current_streak,
            "weekly_completed": len(weekly_days_completed),
            "weekly_days_completed": weekly_days_completed,
        }
    )


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

PROGRAM_JSON_PROMPT = """
You are Angrit AI Coach. Generate a personalized 12-week workout program in STRICT JSON only.

Output rules:
- Return one JSON object with these top-level keys only:
    - "split_name": short string
    - "weeks": array with exactly 12 items (weeks 1..12)
- Each week object must contain:
    - "week": integer (1 to 12)
    - "focus": short string
    - "days": array of 4 to 6 day objects
- Each day object must contain:
    - "day": string (e.g., "Day 1")
    - "workout": short string (e.g., "Upper Body Strength")
    - "exercises": array of 4 to 8 exercise names (strings)
- Keep it realistic and progressive for the user's fitness level.
- Include warm-up, recovery, and deload considerations naturally across weeks.
- No markdown, no code fences, no extra keys, no prose.
"""


def _resolve_gemini_credentials():
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

    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "(missing/invalid)"
    return api_key, model_name, key_source, model_source, masked_key


def _extract_first_json_block(text):
    start_indices = [index for index in (text.find("{"), text.find("[")) if index >= 0]
    if not start_indices:
        return None

    start = min(start_indices)
    opening = text[start]
    closing = "}" if opening == "{" else "]"
    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None


def _extract_program_payload(text):
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("Model returned an empty response.")

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        json_block = _extract_first_json_block(cleaned)
        if not json_block:
            raise
        data = json.loads(json_block)

    if isinstance(data, list):
        weeks = data
        split_name = "AI Generated Split"
    elif isinstance(data, dict):
        weeks = data.get("weeks")
        split_name = (data.get("split_name") or "AI Generated Split").strip()
    else:
        raise ValueError("Model response is not valid JSON program data.")

    if not isinstance(weeks, list):
        raise ValueError("Model response missing 'weeks' array.")
    if len(weeks) != 12:
        raise ValueError("Model response must contain exactly 12 weeks.")

    return {
        "split_name": split_name or "AI Generated Split",
        "weeks": weeks,
    }


def _build_program_name(week_number, day_index, day_payload):
    day_name = (day_payload.get("day") or f"Day {day_index + 1}").strip()
    workout_name = (day_payload.get("workout") or "Workout").strip()
    return f"Week {week_number} - {day_name}: {workout_name}"[:120]


def _to_json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _to_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_safe(item) for item in value]
    return value


def _persist_generated_program(user, split_name, weeks):
    with transaction.atomic():
        split = WorkoutSplit.objects.create(
            user=user,
            name=(split_name or "AI Generated Split")[:120],
        )

        program_order = 0
        for week_index, week in enumerate(weeks):
            week_number = week.get("week") if isinstance(week, dict) else None
            week_number = week_number if isinstance(week_number, int) else (week_index + 1)
            days = week.get("days") if isinstance(week, dict) else []
            if not isinstance(days, list):
                continue

            for day_index, day in enumerate(days):
                if not isinstance(day, dict):
                    continue

                program = WorkoutProgram.objects.create(
                    split=split,
                    name=_build_program_name(week_number, day_index, day),
                    order=program_order,
                )
                program_order += 1

                exercises = day.get("exercises") or []
                if not isinstance(exercises, list):
                    continue

                for exercise_index, exercise_name in enumerate(exercises):
                    cleaned_exercise = str(exercise_name).strip()
                    if not cleaned_exercise:
                        continue
                    WorkoutProgramExercise.objects.create(
                        program=program,
                        exercise_name=cleaned_exercise[:120],
                        order=exercise_index,
                    )

    return split


def _build_program_context(request):
    profile = getattr(request.user, "profile", None)
    goal = getattr(profile, "fitness_goal", "GENERAL_FITNESS") if profile else "GENERAL_FITNESS"
    level = getattr(profile, "fitness_level", "BEGINNER") if profile else "BEGINNER"
    age = getattr(profile, "age", None) if profile else None
    height_cm = getattr(profile, "height_cm", None) if profile else None
    weight_kg = getattr(profile, "weight_kg", None) if profile else None
    recent_logs = list(
        WorkoutLog.objects.filter(user=request.user)
        .order_by("-date", "-created_at")
        .values("exercise", "sets", "reps", "weight", "date")[:20]
    )
    
    existing_splits = list(
        WorkoutSplit.objects.filter(user=request.user)
        .order_by("-updated_at")
        .values("name")[:10]
    )
    available_exercises = list(
        Exercise.objects.all().order_by("exercise_name").values_list("exercise_name", flat=True)[:200]
    )

    requirements = request.data.get("requirements")

    return _to_json_safe({
        "username": request.user.username,
        "fitness_goal": goal,
        "fitness_level": level,
        "age": age,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "available_exercises": available_exercises,
        "recent_workout_logs": recent_logs,
        "existing_split_names": [split["name"] for split in existing_splits],
        "requirements": requirements or "",
    })


def _parse_conversation_id(raw_value):
    if raw_value is None or raw_value == "":
        return None
    if isinstance(raw_value, int):
        return raw_value

    value = str(raw_value).strip()
    if not value:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        raise serializers.ValidationError({"detail": "conversation_id must be an integer."})


def _remaining_free_messages(profile):
    if profile.is_premium:
        return None
    return max(0, FREE_CHAT_MESSAGE_LIMIT - int(profile.free_chat_messages_used or 0))


def _build_chat_prompt(previous_messages, user_message):
    prompt_lines = [SYSTEM_PROMPT.strip(), "", "Conversation history:"]
    if previous_messages:
        for message in previous_messages:
            speaker = "User" if message.role == ChatMessage.ROLE_USER else "Coach"
            prompt_lines.append(f"{speaker}: {message.content}")
    else:
        prompt_lines.append("(no previous messages)")

    prompt_lines.extend(["", f"User: {user_message}", "Coach:"])
    return "\n".join(prompt_lines)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chat_history(request):
    conversation_id = _parse_conversation_id(request.query_params.get("conversation_id"))
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    conversations_qs = ChatConversation.objects.filter(user=request.user)
    active_conversation = None
    if conversation_id is not None:
        active_conversation = get_object_or_404(conversations_qs, pk=conversation_id)
    else:
        active_conversation = conversations_qs.first()

    messages = []
    if active_conversation:
        recent_messages = list(
            active_conversation.messages.order_by("-created_at", "-id")[:CHAT_HISTORY_RESPONSE_LIMIT]
        )
        messages = list(reversed(recent_messages))

    return Response(
        {
            "is_premium": profile.is_premium,
            "remaining_free_messages": _remaining_free_messages(profile),
            "conversations": ChatConversationSerializer(conversations_qs[:20], many=True).data,
            "active_conversation": (
                ChatConversationSerializer(active_conversation).data if active_conversation else None
            ),
            "messages": ChatMessageSerializer(messages, many=True).data,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat_view(request):
    user_message = (request.data.get("message") or "").strip()
    if not user_message:
        return Response({"error": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

    conversation_id = _parse_conversation_id(request.data.get("conversation_id"))
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_premium and _remaining_free_messages(profile) <= 0:
        return Response(
            {
                "error": "Free chat limit reached. Upgrade to premium for unlimited messages.",
                "is_premium": False,
                "remaining_free_messages": 0,
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    conversation = None
    previous_messages = []
    if conversation_id is not None:
        conversation = get_object_or_404(ChatConversation, pk=conversation_id, user=request.user)
        previous_messages = list(
            reversed(
                list(
                    conversation.messages.order_by("-created_at", "-id")[:CHAT_HISTORY_CONTEXT_LIMIT]
                )
            )
        )

    api_key, model_name, key_source, model_source, masked_key = _resolve_gemini_credentials()
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
        prompt = _build_chat_prompt(previous_messages, user_message)

        result = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        reply_text = (getattr(result, "text", None) or "").strip()
        if not reply_text:
            return Response({"error": "Model returned an empty response."}, status=status.HTTP_502_BAD_GATEWAY)

        with transaction.atomic():
            profile = UserProfile.objects.select_for_update().get(pk=profile.pk)
            if not profile.is_premium and _remaining_free_messages(profile) <= 0:
                return Response(
                    {
                        "error": "Free chat limit reached. Upgrade to premium for unlimited messages.",
                        "is_premium": False,
                        "remaining_free_messages": 0,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            if conversation is None:
                conversation = ChatConversation.objects.create(
                    user=request.user,
                    title=user_message[:120] or "New chat",
                )

            ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.ROLE_USER,
                content=user_message,
            )
            ChatMessage.objects.create(
                conversation=conversation,
                role=ChatMessage.ROLE_ASSISTANT,
                content=reply_text,
            )

            if not profile.is_premium:
                profile.free_chat_messages_used += 1
                profile.save(update_fields=["free_chat_messages_used"])

            conversation.save(update_fields=["updated_at"])

            return Response(
                {
                    "reply": reply_text,
                    "conversation_id": conversation.id,
                    "is_premium": profile.is_premium,
                    "remaining_free_messages": _remaining_free_messages(profile),
                },
                status=status.HTTP_200_OK,
            )

    except Exception as e:
        logger.exception("Gemini request failed")
        return Response({"error": f"Gemini request failed: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_training_program(request):
    api_key, model_name, key_source, model_source, masked_key = _resolve_gemini_credentials()
    print(
        f"[generate_training_program] Gemini key source={key_source}, key={masked_key}, "
        f"model source={model_source}, model={model_name}"
    )

    if not api_key:
        return Response(
            {"detail": "Server misconfiguration: GEMINI_API_KEY is missing."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    profile_context = _build_program_context(request)
    prompt = (
        f"{PROGRAM_JSON_PROMPT}\n\n"
        f"User context (JSON):\n{json.dumps(profile_context, ensure_ascii=False)}\n\n"
        "Generate the program now."
    )

    try:
        client = genai.Client(api_key=api_key)
        result = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        raw_text = (getattr(result, "text", None) or "").strip()
        generated_program = _extract_program_payload(raw_text)
        created_split = _persist_generated_program(
            user=request.user,
            split_name=generated_program.get("split_name"),
            weeks=generated_program.get("weeks", []),
        )
        return Response(
            {
                "split": {
                    "id": created_split.id,
                    "name": created_split.name,
                },
                "weeks": generated_program.get("weeks", []),
            },
            status=status.HTTP_200_OK,
        )
    except json.JSONDecodeError:
        logger.exception("Gemini returned invalid JSON")
        return Response(
            {"detail": "AI returned invalid JSON format. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except ValueError as error:
        logger.exception("Gemini returned invalid program shape")
        return Response(
            {"detail": f"AI returned invalid program shape: {str(error)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except Exception as error:
        logger.exception("Program generation failed")
        return Response(
            {"detail": f"Program generation failed: {str(error)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )