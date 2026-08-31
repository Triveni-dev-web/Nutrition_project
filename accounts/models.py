from django.db import models
class FoodEntry(models.Model):
    date = models.DateField()
    meal_type = models.CharField(max_length=20)
    food_name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.food_name} - {self.meal_type}"
# Create your models here.
