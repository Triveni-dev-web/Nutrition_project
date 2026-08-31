from django.urls import path
from .import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/",views.user_login,name="login"),
    path("",views.home,name="home"),
    path("nutrition/", views.nutrition, name="nutrition"),
    path("food-diary/", views.food_diary, name="food_diary"),
    path("food-diary/edit/<int:entry_id>/", views.edit_food,name="edit_food"),
    path("symptoms/",views.symptoms,name="symptoms"),
    path("health-profile/",views.health_profile,name="health_profile"),
]