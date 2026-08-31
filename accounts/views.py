from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

import pandas as pd
import os
import requests

from dotenv import load_dotenv

from .models import FoodEntry,Symptom, HealthProfile
from django.utils import timezone
from django.conf import settings


# =========================================================
# ENVIRONMENT / USDA API
# =========================================================

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")

print("API KEY LOADED:", bool(USDA_API_KEY))


# =========================================================
# USDA NUTRITION API
# =========================================================

def get_nutrition(food_name):

    url = "https://api.nal.usda.gov/fdc/v1/foods/search"

    params = {
        "api_key": USDA_API_KEY,
        "query": food_name,
        "pageSize": 1
    }

    response = requests.get(
        url,
        params=params
    )

    print("STATUS:", response.status_code)

    # -----------------------------------------------------
    # API ERROR
    # -----------------------------------------------------

    if response.status_code != 200:

        print("USDA API Error:", response.status_code)
        print(response.text)

        return None

    # -----------------------------------------------------
    # GET RESPONSE DATA
    # -----------------------------------------------------

    data = response.json()

    if not data.get("foods"):

        print("No food found")

        return None

    food = data["foods"][0]

    print(
        "FOOD:",
        food.get("description")
    )

    # -----------------------------------------------------
    # INITIAL NUTRITION VALUES
    # -----------------------------------------------------

    calories = 0
    protein = 0
    carbohydrates = 0

    # -----------------------------------------------------
    # READ NUTRIENTS
    # -----------------------------------------------------

    for nutrient in food.get("foodNutrients", []):

        nutrient_id = nutrient.get("nutrientId")

        nutrient_name = nutrient.get(
            "nutrientName",
            ""
        ).lower()

        value = nutrient.get(
            "value",
            0
        ) or 0

        # Calories / Energy
        if (
            nutrient_id in [1008, 2047, 2048]
            or "energy" in nutrient_name
        ):

            calories = value

        # Protein
        elif (
            nutrient_id == 1003
            or "protein" in nutrient_name
        ):

            protein = value

        # Carbohydrates
        elif (
            nutrient_id == 1005
            or "carbohydrate" in nutrient_name
        ):

            carbohydrates = value

    # -----------------------------------------------------
    # PRINT RESULTS FOR TESTING
    # -----------------------------------------------------

    print(
        "CALORIES:",
        calories
    )

    print(
        "PROTEIN:",
        protein
    )

    print(
        "CARBS:",
        carbohydrates
    )

    # -----------------------------------------------------
    # RETURN NUTRITION DATA
    # -----------------------------------------------------

    return {
        "food_name": food.get(
            "description"
        ),

        "calories": calories,

        "protein": protein,

        "carbohydrates": carbohydrates
    }


# =========================================================
# HOME
# =========================================================

def home(request):

    return render(
        request,
        "accounts/home.html"
    )


# =========================================================
# REGISTER
# =========================================================

def register(request):

    if request.method == "POST":

        form = UserCreationForm(
            request.POST
        )

        if form.is_valid():

            user = form.save()

            login(
                request,
                user
            )

            return redirect(
                "nutrition"
            )

    else:

        form = UserCreationForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


# =========================================================
# LOGIN
# =========================================================

def user_login(request):

    if request.method == "POST":

        username = request.POST.get(
            "username"
        )

        password = request.POST.get(
            "password"
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            return redirect(
                "nutrition"
            )

        else:

            return render(
                request,
                "accounts/login.html",
                {
                    "error":
                        "Invalid username or password"
                }
            )

    return render(
        request,
        "accounts/login.html"
    )


# =========================================================
# NUTRITION
# =========================================================

def nutrition(request):
    profile=HealthProfile.objects.last()

    if request.method == "POST":

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        age = request.POST.get("age")

        gender = request.POST.get("gender")

        height = request.POST.get("height")

        weight = request.POST.get("weight")

        activity = request.POST.get("activity")

        goal = request.POST.get("goal")

        diet = request.POST.get("diet")

        medical_conditions = request.POST.get(
            "medical_conditions"
        )

        dietary_restrictions = request.POST.get(
            "dietary_restrictions"
        )

        # -------------------------------------------------
        # LOAD EXCEL DATABASE
        # -------------------------------------------------

        file_path = os.path.join(
            settings.BASE_DIR,
            "nutrition_food_database.xlsx"
        )

        food = pd.read_excel(
            file_path
        )

        # -------------------------------------------------
        # CLEAN COLUMN NAMES
        # -------------------------------------------------

        food.columns = (
            food.columns
            .str.strip()
        )

        # -------------------------------------------------
        # VEGETARIAN FILTER
        # -------------------------------------------------

        if diet == "Vegetarian":

            food = food[
                ~food["food_name"]
                .astype(str)
                .str.contains(
                    "chicken|fish|meat|mutton|prawn|egg",
                    case=False,
                    na=False
                )
            ]

            food = food[
                ~food["category"]
                .astype(str)
                .str.contains(
                    "meat",
                    case=False,
                    na=False
                )
            ]

        # -------------------------------------------------
        # VEGAN FILTER
        # -------------------------------------------------

        elif diet == "Vegan":

            food = food[
                ~food["food_name"]
                .astype(str)
                .str.contains(
                    "chicken|fish|meat|mutton|prawn|egg|paneer|curd|yogurt|milk|ghee|butter|cheese|ice cream",
                    case=False,
                    na=False
                )
            ]

            food = food[
                ~food["category"]
                .astype(str)
                .str.contains(
                    "meat|dairy",
                    case=False,
                    na=False
                )
            ]

        # -------------------------------------------------
        # NON-VEGETARIAN
        # -------------------------------------------------

        elif diet == "Non-Vegetarian":

            pass

        # -------------------------------------------------
        # FIND CALORIE COLUMN
        # -------------------------------------------------

        calorie_column = None

        for column in food.columns:

            if "calorie" in column.lower():

                calorie_column = column

                break

        # -------------------------------------------------
        # GOAL FILTER
        # -------------------------------------------------

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

        # -------------------------------------------------
        # TOP 5 RECOMMENDED FOODS
        # -------------------------------------------------

        recommended_foods = (
            food.head(5)
            .to_dict("records")
        )

        # =================================================
        # TEXT RECOMMENDATIONS
        # =================================================

        recommendations = []

        # -------------------------------------------------
        # HEALTH GOAL
        # -------------------------------------------------

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

        # -------------------------------------------------
        # ACTIVITY LEVEL
        # -------------------------------------------------

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

        # -------------------------------------------------
        # DIET PREFERENCE
        # -------------------------------------------------

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

        # -------------------------------------------------
        # SEND DATA TO HTML
        # -------------------------------------------------

        return render(
    request,
    "accounts/nutrition.html",
    {
        "age": profile.age if profile else "",
        "gender": profile.gender if profile else "",
        "height": profile.height if profile else "",
        "weight": profile.weight if profile else "",
        "activity": profile.activity if profile else "",
        "goal": profile.goal if profile else "",
        "diet": profile.diet if profile else "",
        "medical_conditions": profile.medical_conditions if profile else "",
        "dietary_restrictions": profile.dietary_restrictions if profile else "",
        "recommended_foods": recommended_foods,
        "recommendations": recommendations,
    }
)

    
    # -------------------------------
    # FIRST PAGE LOAD
    # -------------------------------

    return render(
    request,
    "accounts/nutrition.html",
    {
        "age": profile.age if profile else "",
        "gender": profile.gender if profile else "",
        "height": profile.height if profile else "",
        "weight": profile.weight if profile else "",
        "activity": profile.activity if profile else "",
        "goal": profile.goal if profile else "",
        "diet": profile.diet if profile else "",
        "medical_conditions": profile.medical_conditions if profile else "",
        "dietary_restrictions": profile.dietary_restrictions if profile else "",
    }
)
   


# =========================================================
# FOOD DIARY
# =========================================================

def food_diary(request):

    # =====================================================
    # POST REQUEST
    # =====================================================

    if request.method == "POST":

        action = request.POST.get(
            "action"
        )

        entry_id = request.POST.get(
            "entry_id"
        )

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

            return redirect(
                "food_diary"
            )

        # =================================================
        # EDIT
        # =================================================

        elif action == "edit":

            if entry_id:

                entry = get_object_or_404(
                    FoodEntry,
                    id=entry_id
                )

                date = request.POST.get(
                    "date"
                )

                meal_type = request.POST.get(
                    "meal_type"
                )

                food_name = request.POST.get(
                    "food_name"
                )

                quantity = request.POST.get(
                    "quantity"
                )

                if date:

                    entry.date = date

                if meal_type:

                    entry.meal_type = meal_type

                if food_name:

                    entry.food_name = food_name

                if quantity:

                    entry.quantity = quantity

                entry.save()

            return redirect(
                "food_diary"
            )

        # =================================================
        # ADD
        # =================================================

        else:

            date = request.POST.get(
                "date"
            )

            meal_type = request.POST.get(
                "meal_type"
            )

            food_name = request.POST.get(
                "food_name"
            )

            quantity = request.POST.get(
                "quantity"
            )

            if not date:

                date = timezone.localdate()

            # -------------------------------------------------
            # GET NUTRITION FROM USDA
            # -------------------------------------------------

            nutrition_data = get_nutrition(
                food_name
            )

            # -------------------------------------------------
            # CREATE FOOD ENTRY
            # -------------------------------------------------

            FoodEntry.objects.create(

                date=date,

                meal_type=meal_type,

                food_name=food_name,

                quantity=quantity,

                calories=(
                    nutrition_data["calories"]
                    if nutrition_data
                    else 0
                ),

                protein=(
                    nutrition_data["protein"]
                    if nutrition_data
                    else 0
                ),

                carbohydrates=(
                    nutrition_data["carbohydrates"]
                    if nutrition_data
                    else 0
                )
            )

            return redirect(
                "food_diary"
            )

    # =====================================================
    # DISPLAY FOOD ENTRIES
    # =====================================================

    entries = (
        FoodEntry.objects
        .all()
        .order_by(
            "-date",
            "-id"
        )
    )
    total_calories = sum(entry.calories or 0 for entry in entries)
    total_protein = sum(entry.protein or 0 for entry in entries)
    total_carbohydrates = sum(entry.carbohydrates or 0 for entry in entries)

    return render(
        request,
        "accounts/food_diary.html",
        {
            "entries": entries,
            "total_calories":total_calories,
            "total_protein":total_protein,
            "total_carbohydrates":total_carbohydrates
        }
    )


# =========================================================
# EDIT FOOD — SEPARATE PAGE
# =========================================================

def edit_food(request, entry_id):

    entry = get_object_or_404(
        FoodEntry,
        id=entry_id
    )

    if request.method == "POST":

        entry.date = request.POST.get(
            "date"
        )

        entry.meal_type = request.POST.get(
            "meal_type"
        )

        entry.food_name = request.POST.get(
            "food_name"
        )

        entry.quantity = request.POST.get(
            "quantity"
        )

        entry.save()

        return redirect(
            "food_diary"
        )

    return render(
        request,
        "accounts/edit_food.html",
        {
            "entry": entry
        }
    )
# ================= SYMPTOMS =================

def symptoms(request):

    if request.method == "POST":

        action = request.POST.get("action")
        symptom_id = request.POST.get("symptom_id")

        # DELETE
        if action == "delete":

            symptom = get_object_or_404(
                Symptom,
                id=symptom_id
            )

            symptom.delete()

            return redirect("symptoms")

        # EDIT
        elif action == "edit":

            symptom = get_object_or_404(
                Symptom,
                id=symptom_id
            )

            symptom.name = request.POST.get("name")
            symptom.severity = request.POST.get("severity")

            symptom.save()

            return redirect("symptoms")

        # ADD
        else:

            symptom_names = request.POST.getlist("symptoms")
            severity = request.POST.get("severity")

            for name in symptom_names:

                Symptom.objects.create(
                    name=name,
                    severity=severity
                )

            return redirect("symptoms")

    symptoms_list = Symptom.objects.all().order_by(
        "-date",
        "-id"
    )

    return render(
        request,
        "accounts/symptoms.html",
        {
            "symptoms": symptoms_list
        }
    )
# ================= HEALTH PROFILE =================

# ================= HEALTH PROFILE =================

def health_profile(request):

    profile = HealthProfile.objects.last()

    if request.method == "POST":

        if profile:
            profile.age = request.POST.get("age")
            profile.gender = request.POST.get("gender")
            profile.height = request.POST.get("height")
            profile.weight = request.POST.get("weight")
            profile.activity = request.POST.get("activity")
            profile.goal = request.POST.get("goal")
            profile.diet = request.POST.get("diet")
            profile.medical_conditions = request.POST.get("medical_conditions")
            profile.dietary_restrictions = request.POST.get("dietary_restrictions")

            profile.save()

        else:
            profile = HealthProfile.objects.create(
                age=request.POST.get("age"),
                gender=request.POST.get("gender"),
                height=request.POST.get("height"),
                weight=request.POST.get("weight"),
                activity=request.POST.get("activity"),
                goal=request.POST.get("goal"),
                diet=request.POST.get("diet"),
                medical_conditions=request.POST.get("medical_conditions"),
                dietary_restrictions=request.POST.get("dietary_restrictions"),
            )

        return redirect("health_profile")

    return render(
        request,
        "accounts/health_profile.html",
        {
            "profile": profile
        }
    )