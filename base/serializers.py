from rest_framework import serializers
from .models import Exercise, UserProfile


def is_valid_youtube_url(url: str) -> bool:
    if not url:
        return False
    value = url.lower()
    return "youtube.com" in value or "youtu.be" in value

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "username", "email", "age", "height_cm", "weight_kg",
            "fitness_goal", "fitness_level", "is_premium"
        ]

    #serializers used to pass frontend data to backend

class ExerciseListSerializer(serializers.ModelSerializer):
    short_description = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            "id",
            "exercise_name",
            "category",
            "difficulty_level",
            "short_description",
            "video_url",
            "is_premium",
        ]

    def get_short_description(self, obj):
        if not obj.description:
            return ""
        return obj.description[:140].strip()


class ExerciseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            "id",
            "exercise_name",
            "description",
            "category",
            "difficulty_level",
            "video_url",
            "muscle_groups_targeted",
            "equipment_needed",
            "is_premium",
        ]


class ExerciseAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            "id",
            "exercise_name",
            "description",
            "category",
            "difficulty_level",
            "video_url",
            "muscle_groups_targeted",
            "equipment_needed",
            "is_premium",
        ]

    def validate_video_url(self, value):
        if not is_valid_youtube_url(value):
            raise serializers.ValidationError("video_url must be a valid YouTube URL.")
        return value