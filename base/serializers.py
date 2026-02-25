from rest_framework import serializers
from .models import Exercise, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "username", "email", "age", "height_cm", "weight_kg",
            "fitness_goal", "fitness_level"
        ]

    #serializers used to pass frontend data to backend

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "name", "category", "difficulty", "muscle_group", "tutorial_url", "is_premium"] 