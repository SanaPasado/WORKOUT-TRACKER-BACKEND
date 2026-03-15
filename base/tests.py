from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.models import DifficultyLevel, Exercise, ExerciseCategory, UserProfile


class ExerciseApiTests(APITestCase):
	def setUp(self):
		self.exercise = Exercise.objects.create(
			exercise_name="Bench Press",
			description="A heavy compound pressing movement for upper-body strength.",
			category=ExerciseCategory.STRENGTH,
			difficulty_level=DifficultyLevel.MEDIUM,
			video_url="https://www.youtube.com/watch?v=tuwHzzPdaGc",
			muscle_groups_targeted="Chest, triceps, shoulders",
			equipment_needed="Barbell, bench",
		)

		self.free_user = User.objects.create_user(username="free", password="Password123!")
		self.premium_user = User.objects.create_user(username="premium", password="Password123!")
		self.admin_user = User.objects.create_user(
			username="admin",
			password="Password123!",
			is_staff=True,
		)

		UserProfile.objects.filter(user=self.premium_user).update(is_premium=True)

	def test_public_exercise_list_returns_basic_fields(self):
		response = self.client.get(reverse("exercise-list"))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertSetEqual(
			set(response.data[0].keys()),
			{
				"id",
				"exercise_name",
				"category",
				"difficulty_level",
				"short_description",
				"video_url",
			},
		)

	def test_free_user_cannot_view_exercise_details(self):
		self.client.force_authenticate(user=self.free_user)

		response = self.client.get(reverse("exercise-detail", args=[self.exercise.id]))

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_premium_user_can_view_exercise_details(self):
		self.client.force_authenticate(user=self.premium_user)

		response = self.client.get(reverse("exercise-detail", args=[self.exercise.id]))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["exercise_name"], self.exercise.exercise_name)
		self.assertEqual(response.data["equipment_needed"], self.exercise.equipment_needed)

	def test_admin_can_create_exercise(self):
		self.client.force_authenticate(user=self.admin_user)
		payload = {
			"exercise_name": "Assault Bike Sprints",
			"description": "High-output intervals for anaerobic conditioning.",
			"category": ExerciseCategory.CARDIO,
			"difficulty_level": DifficultyLevel.HARD,
			"video_url": "https://youtu.be/bfLHTLQZ5nc",
			"muscle_groups_targeted": "Legs, lungs",
			"equipment_needed": "Assault bike",
		}

		response = self.client.post(reverse("exercise-list"), payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Exercise.objects.filter(exercise_name="Assault Bike Sprints").exists())

	def test_admin_create_rejects_non_youtube_url(self):
		self.client.force_authenticate(user=self.admin_user)
		payload = {
			"exercise_name": "Invalid Exercise",
			"description": "Should fail validation.",
			"category": ExerciseCategory.CARDIO,
			"difficulty_level": DifficultyLevel.EASY,
			"video_url": "https://vimeo.com/12345",
		}

		response = self.client.post(reverse("exercise-list"), payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("video_url", response.data)
