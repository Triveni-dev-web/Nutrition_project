from django.db import models


# ================= FOOD ENTRY =================

class FoodEntry(models.Model):
    date = models.DateField()
    meal_type = models.CharField(max_length=20)
    food_name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)

    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbohydrates = models.FloatField(default=0)

    def __str__(self):
        return f"{self.food_name} - {self.meal_type}"


# ================= SYMPTOM =================

class Symptom(models.Model):
    name = models.CharField(max_length=100)
    severity = models.CharField(max_length=20)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.severity}"
# ================= HEALTH PROFILE =================

class HealthProfile(models.Model):

    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    height = models.FloatField()
    weight = models.FloatField()

    activity = models.CharField(max_length=30)
    goal = models.CharField(max_length=30)
    diet = models.CharField(max_length=30)

    medical_conditions = models.TextField(
        blank=True
    )

    dietary_restrictions = models.TextField(
        blank=True
    )

    def __str__(self):
        return f"Health Profile - {self.age}"    