from django.contrib import admin
from .models import Exercise

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("exercise_name", "category", "difficulty_level")
    search_fields = ("exercise_name", "category")
