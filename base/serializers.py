from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "display_name", "email", "age", "height_cm", "weight_kg",
            "fitness_goal", "fitness_level"
        ]

    #serializers used to pass frontend data to backend