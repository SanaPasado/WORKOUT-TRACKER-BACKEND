from django.contrib import admin
from .models import Exercise, UserProfile



@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
	list_display = ("exercise_name", "category", "difficulty_level", "is_premium")
	list_filter = ("category", "difficulty_level", "is_premium")
	search_fields = ("exercise_name", "muscle_groups_targeted", "equipment_needed")
	ordering = ("exercise_name",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "fitness_goal", "fitness_level", "is_premium")
	list_filter = ("fitness_goal", "fitness_level", "is_premium")
	search_fields = ("user__username", "user__email")
