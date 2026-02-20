from django.db import models

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

class User(models.Model):
    user_name = models.CharField(max_length=30)
    email = models.EmailField(max_length = 30)
    password  = models.CharField(max_length=30)

class UserProfile(models.Model):
    age = models.PositiveIntegerField
    user_profile = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    height = models.DecimalField()
    weight = models.DecimalField()
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fitness_goal = models.CharField(max_length=32, choices=FitnessGoal.choices, default=FitnessGoal.GENERAL_FITNESS)
    fitness_level = models.CharField(max_length=16, choices=FitnessLevel.choices, default=FitnessLevel.BEGINNER)

    

# basically pag pumili si user ng choice sa frontend , tatanggapin nya maski caps or not
# lahat to for the user profile page 



class ExerciseCategory(models.TextChoices):
    CHEST = "CHEST", "Chest"
    BACK = "BACK", "Back"
    SHOULDERS = "SHOULDERS", "Shoulders"
    ARMS = "ARMS", "Arms"
    LEGS = "LEGS", "Legs"
    CORE = "CORE", "Core"
    CARDIO = "CARDIO", "Cardio"

class Difficulty(models.TextChoices):
    BEGINNER = "BEGINNER", "Beginner"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    ADVANCED = "ADVANCED", "Advanced"

class Exercise(models.Model):
    name = models.CharField(max_length=120, unique=True)
    category = models.CharField(max_length=20, choices=ExerciseCategory.choices)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices)
    muscle_group = models.CharField(max_length=120)
    is_premium = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # optional
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
# This one for exercise list

