from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

import pandas as pd
import os

from .models import FoodEntry
from django.utils import timezone
from django.conf import settings


# ================= HOME =================

def home(request):
    return render(request, "accounts/home.html")


# ================= REGISTER =================

def register(request):

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("nutrition")

    else:

        form = UserCreationForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )


# ================= LOGIN =================

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("nutrition")

        else:

            return render(
                request,
                "accounts/login.html",
                {
                    "error": "Invalid username or password"
                }
            )

    return render(
        request,
        "accounts/login.html"
    )


# ================= NUTRITION =================

def nutrition(request):

    if request.method == "POST":

        # -------- GET FORM DATA --------

        age = request.POST.get("age")
        gender = request.POST.get("gender")
        height = request.POST.get("height")
        weight = request.POST.get("weight")
        activity = request.POST.get("activity")
        goal = request.POST.get("goal")
        diet = request.POST.get("diet")
        medical_conditions = request.POST.get("medical_conditions")
        dietary_restrictions = request.POST.get("dietary_restrictions")


        # -------- LOAD EXCEL DATABASE --------

        file_path = os.path.join(
            settings.BASE_DIR,
            "nutrition_food_database.xlsx"
        )

        food = pd.read_excel(file_path)


        # -------- CLEAN COLUMN NAMES --------

        food.columns = food.columns.str.strip()


        # -------- DIET FILTER --------

        if diet == "Vegetarian":

            food = food[
                ~food["food_name"].astype(str).str.contains(
                    "chicken|fish|meat|mutton|prawn|egg",
                    case=False,
                    na=False
                )
            ]

            food = food[
                ~food["category"].astype(str).str.contains(
                    "meat",
                    case=False,
                    na=False
                )
            ]


        elif diet == "Vegan":

            food = food[
                ~food["food_name"].astype(str).str.contains(
                    "chicken|fish|meat|mutton|prawn|egg|paneer|curd|yogurt|milk|ghee|butter|cheese|ice cream",
                    case=False,
                    na=False
                )
            ]

            food = food[
                ~food["category"].astype(str).str.contains(
                    "meat|dairy",
                    case=False,
                    na=False
                )
            ]


        elif diet == "Non-Vegetarian":

            pass


        # -------- FIND CALORIE COLUMN --------

        calorie_column = None

        for column in food.columns:

            if "calorie" in column.lower():

                calorie_column = column

                break


        # -------- GOAL FILTER --------

        if calorie_column:

            if goal == "Weight Loss":

                food = food.sort_values(
                    by=calorie_column,
                    ascending=True
                )

            elif goal == "Weight Gain":

                food = food.sort_values(
                    by=calorie_column,
                    ascending=False
                )

            elif goal == "Maintain Weight":

                food = food.sort_values(
                    by=calorie_column,
                    ascending=True
                )


        # -------- SELECT TOP 5 FOODS --------

        recommended_foods = food.head(5).to_dict(
            "records"
        )


        # ================= TEXT RECOMMENDATIONS =================

        recommendations = []


        # -------- HEALTH GOAL --------

        if goal == "Weight Loss":

            recommendations.append(
                "Choose low-calorie foods and eat more vegetables"
            )

            recommendations.append(
                "Avoid excess sugar and fried foods"
            )


        elif goal == "Weight Gain":

            recommendations.append(
                "Eat calorie-rich and nutritious foods"
            )

            recommendations.append(
                "Include protein in every meal"
            )


        else:

            recommendations.append(
                "Maintain a balanced diet"
            )

            recommendations.append(
                "Eat vegetables, fruits and whole grains"
            )


        # -------- ACTIVITY LEVEL --------

        if activity == "Low":

            recommendations.append(
                "Include light exercise such as walking"
            )

        elif activity == "Moderate":

            recommendations.append(
                "Exercise regularly for better fitness"
            )

        elif activity == "High":

            recommendations.append(
                "Include regular cardio and strength exercises"
            )


        # -------- DIET PREFERENCE --------

        if diet == "Vegetarian":

            recommendations.append(
                "Include dal, paneer, beans and vegetables"
            )

        elif diet == "Non-Vegetarian":

            recommendations.append(
                "Include eggs, fish or lean meat for protein"
            )

        elif diet == "Vegan":

            recommendations.append(
                "Include beans, lentils, tofu and nuts"
            )


        # -------- SEND DATA TO HTML --------

        return render(
            request,
            "accounts/nutrition.html",
            {
                "age": age,
                "gender": gender,
                "height": height,
                "weight": weight,
                "activity": activity,
                "goal": goal,
                "diet": diet,
                "recommendations": recommendations,
                "recommended_foods": recommended_foods,
                "message": "Your nutrition details were submitted successfully!"
            }
        )


    # -------- FIRST PAGE LOAD --------

    return render(
        request,
        "accounts/nutrition.html"
    )


# =========================================================
# ================= FOOD DIARY ===========================
# =========================================================

def food_diary(request):

    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get("action")
        entry_id = request.POST.get("entry_id")


        # =================================================
        # DELETE
        # =================================================

        if action == "delete":

            if entry_id:

                entry = get_object_or_404(
                    FoodEntry,
                    id=entry_id
                )

                entry.delete()

            return redirect("food_diary")


        # =================================================
        # EDIT
        # =================================================

        elif action == "edit":

            if entry_id:

                entry = get_object_or_404(
                    FoodEntry,
                    id=entry_id
                )

                # Get edited values
                date = request.POST.get("date")
                meal_type = request.POST.get("meal_type")
                food_name = request.POST.get("food_name")
                quantity = request.POST.get("quantity")


                # Update date
                if date:

                    entry.date = date


                # Update meal
                if meal_type:

                    entry.meal_type = meal_type


                # Update food
                if food_name:

                    entry.food_name = food_name


                # Update quantity
                if quantity:

                    entry.quantity = quantity


                # SAVE CHANGES
                entry.save()


            return redirect("food_diary")


        # =================================================
        # ADD
        # =================================================

        else:

            date = request.POST.get("date")
            meal_type = request.POST.get("meal_type")
            food_name = request.POST.get("food_name")
            quantity = request.POST.get("quantity")


            # If date is empty, use today's date
            if not date:

                date = timezone.localdate()


            FoodEntry.objects.create(

                date=date,

                meal_type=meal_type,

                food_name=food_name,

                quantity=quantity

            )


            return redirect("food_diary")


    # =====================================================
    # DISPLAY FOOD ENTRIES
    # =====================================================

    entries = FoodEntry.objects.all().order_by(
        "-date",
        "-id"
    )


    return render(
        request,
        "accounts/food_diary.html",
        {
            "entries": entries
        }
    )
def edit_food(request, entry_id):

    entry = get_object_or_404(FoodEntry, id=entry_id)

    if request.method == "POST":

        entry.date = request.POST.get("date")
        entry.meal_type = request.POST.get("meal_type")
        entry.food_name = request.POST.get("food_name")
        entry.quantity = request.POST.get("quantity")

        entry.save()

        return redirect("food_diary")

    return render(
        request,
        "accounts/edit_food.html",
        {
            "entry": entry
        }
    )