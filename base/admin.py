from django.contrib import admin

from .models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
	list_display = (
		"exercise_name",
		"category",
		"difficulty_level",
		"muscle_groups_targeted",
		"created_at",
	)
	list_filter = ("category", "difficulty_level")
	search_fields = ("exercise_name", "description", "muscle_groups_targeted", "equipment_needed")
	ordering = ("exercise_name", "id")
