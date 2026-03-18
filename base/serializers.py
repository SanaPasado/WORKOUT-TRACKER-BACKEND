from rest_framework import serializers
from .models import (
    ChatConversation,
    ChatMessage,
    DifficultyLevel,
    Exercise,
    ExerciseCategory,
    UserProfile,
    WorkoutLog,
    WorkoutSplit,
    WorkoutProgram,
    WorkoutProgramExercise,
)

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "username", "email", "age", "height_cm", "weight_kg",
            "fitness_goal", "fitness_level", "is_premium", "free_chat_messages_used", "premium_provider",
            "premium_order_id", "premium_since"
        ]
        read_only_fields = [
            "is_premium",
            "free_chat_messages_used",
            "premium_provider",
            "premium_order_id",
            "premium_since",
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
        ]

    def get_short_description(self, obj):
        description = (obj.description or "").strip()
        if len(description) <= 140:
            return description
        return f"{description[:137].rstrip()}..."


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
            "created_at",
            "updated_at",
        ]


class ExerciseWriteSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        cleaned_attrs = attrs.copy()

        for field_name in [
            "exercise_name",
            "description",
            "video_url",
            "muscle_groups_targeted",
            "equipment_needed",
        ]:
            value = cleaned_attrs.get(field_name)
            if isinstance(value, str):
                cleaned_attrs[field_name] = value.strip()

        if not cleaned_attrs.get("exercise_name"):
            raise serializers.ValidationError({"exercise_name": "This field is required."})

        return cleaned_attrs

    def validate_category(self, value):
        valid_values = {choice for choice, _ in ExerciseCategory.choices}
        if value not in valid_values:
            raise serializers.ValidationError("Invalid category selection.")
        return value

    def validate_difficulty_level(self, value):
        valid_values = {choice for choice, _ in DifficultyLevel.choices}
        if value not in valid_values:
            raise serializers.ValidationError("Invalid difficulty level selection.")
        return value


class WorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLog
        fields = ["id", "exercise", "sets", "reps", "weight", "date", "created_at"]
        read_only_fields = ["id", "created_at"]


class WorkoutProgramExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutProgramExercise
        fields = ["id", "exercise_name", "order"]


class WorkoutProgramSerializer(serializers.ModelSerializer):
    exercises = serializers.SerializerMethodField(read_only=True)
    exercise_items = WorkoutProgramExerciseSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = WorkoutProgram
        fields = ["id", "name", "order", "exercises", "exercise_items"]

    def get_exercises(self, obj):
        return [item.exercise_name for item in obj.exercise_items.all()]


class WorkoutSplitSerializer(serializers.ModelSerializer):
    programs = WorkoutProgramSerializer(many=True)

    class Meta:
        model = WorkoutSplit
        fields = ["id", "name", "programs", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def _extract_exercise_items(self, program_payload):
        if "exercise_items" in program_payload:
            return program_payload.get("exercise_items") or []
        exercises = program_payload.get("exercises") or []
        return [
            {
                "exercise_name": exercise_name,
                "order": exercise_index,
            }
            for exercise_index, exercise_name in enumerate(exercises)
            if str(exercise_name).strip()
        ]

    def create(self, validated_data):
        programs_data = validated_data.pop("programs", [])
        split = WorkoutSplit.objects.create(**validated_data)

        for program_index, program_data in enumerate(programs_data):
            exercise_items_data = self._extract_exercise_items(program_data)
            program = WorkoutProgram.objects.create(
                split=split,
                name=program_data.get("name", "").strip(),
                order=program_data.get("order", program_index),
            )
            for exercise_index, exercise_data in enumerate(exercise_items_data):
                exercise_name = (exercise_data.get("exercise_name") or "").strip()
                if not exercise_name:
                    continue
                WorkoutProgramExercise.objects.create(
                    program=program,
                    exercise_name=exercise_name,
                    order=exercise_data.get("order", exercise_index),
                )

        return split

    def update(self, instance, validated_data):
        programs_data = validated_data.pop("programs", None)
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        if programs_data is not None:
            instance.programs.all().delete()
            for program_index, program_data in enumerate(programs_data):
                exercise_items_data = self._extract_exercise_items(program_data)
                program = WorkoutProgram.objects.create(
                    split=instance,
                    name=program_data.get("name", "").strip(),
                    order=program_data.get("order", program_index),
                )
                for exercise_index, exercise_data in enumerate(exercise_items_data):
                    exercise_name = (exercise_data.get("exercise_name") or "").strip()
                    if not exercise_name:
                        continue
                    WorkoutProgramExercise.objects.create(
                        program=program,
                        exercise_name=exercise_name,
                        order=exercise_data.get("order", exercise_index),
                    )

        return instance


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "created_at"]


class ChatConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatConversation
        fields = ["id", "title", "created_at", "updated_at"]