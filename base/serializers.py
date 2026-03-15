from rest_framework import serializers
from .models import (
    Exercise,
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
            "fitness_goal", "fitness_level", "is_premium", "premium_provider",
            "premium_order_id", "premium_since"
        ]
        read_only_fields = ["is_premium", "premium_provider", "premium_order_id", "premium_since"]

    #serializers used to pass frontend data to backend

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = "__all__"


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