from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    def __str__(self):
        return self.user.username

    

# basically pag pumili si user ng choice sa frontend , tatanggapin nya maski caps or not
# lahat to for the user profile page 



class ExerciseCategory(models.TextChoices):
    CARDIO = "cardio", "Cardio"
    STRENGTH = "strength", "Strength"
    STRETCHING = "stretching", "Stretching"
    FLEXIBILITY = "flexibility", "Flexibility"

class Difficulty(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"

class Exercise(models.Model):
    exercise_name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=ExerciseCategory.choices)
    difficulty_level = models.CharField(max_length=20, choices=Difficulty.choices)
    video_url = models.URLField()
    muscle_groups_targeted = models.CharField(max_length=255, blank=True, null=True)
    equipment_needed = models.CharField(max_length=255, blank=True, null=True)
    is_premium = models.BooleanField(default=False)

    class Meta:
        ordering = ["exercise_name"]

    def __str__(self):
        return self.exercise_name
# This one for exercise list


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

