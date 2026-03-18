from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .validators import validate_youtube_url

class FitnessGoal(models.TextChoices):
    BUILD_MUSCLE = "BUILD_MUSCLE", "Build Muscle"
    LOSE_WEIGHT = "LOSE_WEIGHT", "Lose Weight"
    IMPROVE_STRENGTH = "IMPROVE_STRENGTH", "Improve Strength"
    INCREASE_ENDURANCE = "INCREASE_ENDURANCE", "Increase Endurance"
    GENERAL_FITNESS = "GENERAL_FITNESS", "General Fitness"

class FitnessLevel(models.TextChoices):
    BEGINNER = "BEGINNER", "Beginner"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    ADVANCED = "ADVANCED", "Advanced"
    EXPERT = "EXPERT", "Expert"


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    age = models.PositiveIntegerField(null=True, blank=True)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fitness_goal = models.CharField(max_length=32, choices=FitnessGoal.choices, default=FitnessGoal.GENERAL_FITNESS)
    fitness_level = models.CharField(max_length=16, choices=FitnessLevel.choices, default=FitnessLevel.BEGINNER)
    is_premium = models.BooleanField(default=False)
    free_chat_messages_used = models.PositiveIntegerField(default=0)
    premium_provider = models.CharField(max_length=32, blank=True, default="")
    premium_order_id = models.CharField(max_length=100, blank=True, default="")
    premium_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    

# basically pag pumili si user ng choice sa frontend , tatanggapin nya maski caps or not
# lahat to for the user profile page 



class ExerciseCategory(models.TextChoices):
    CARDIO = "cardio", "Cardio"
    STRENGTH = "strength", "Strength"
    STRETCHING = "stretching", "Stretching"
    FLEXIBILITY = "flexibility", "Flexibility"


class DifficultyLevel(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"

class Exercise(models.Model):
    exercise_name = models.CharField(max_length=160, db_index=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=ExerciseCategory.choices, db_index=True)
    difficulty_level = models.CharField(max_length=10, choices=DifficultyLevel.choices, db_index=True)
    video_url = models.URLField(validators=[validate_youtube_url])
    muscle_groups_targeted = models.CharField(max_length=255, blank=True)
    equipment_needed = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["exercise_name", "id"]
        indexes = [
            models.Index(fields=["category", "difficulty_level"]),
        ]

    def __str__(self):
        return self.exercise_name


class WorkoutLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workout_logs")
    exercise = models.CharField(max_length=120)
    sets = models.PositiveIntegerField(default=1)
    reps = models.PositiveIntegerField(default=0)
    weight = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at", "-id"]

    def __str__(self):
        return f"{self.user.username} - {self.exercise} ({self.date})"


class WorkoutSplit(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workout_splits")
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class WorkoutProgram(models.Model):
    split = models.ForeignKey(WorkoutSplit, on_delete=models.CASCADE, related_name="programs")
    name = models.CharField(max_length=120)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


class WorkoutProgramExercise(models.Model):
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name="exercise_items")
    exercise_name = models.CharField(max_length=120)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.exercise_name


class ChatConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_conversations")
    title = models.CharField(max_length=120, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "-created_at", "-id"]

    def __str__(self):
        return f"{self.user.username} chat {self.id}"


class ChatMessage(models.Model):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_ASSISTANT, "Assistant"),
    ]

    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.role} message {self.id}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

