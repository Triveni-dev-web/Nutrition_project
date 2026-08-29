import pandas as pd

food = pd.read_excel("nutrition_food_database.xlsx")

print(food.head())

patient = pd.read_excel("Patient_health_database.xlsx")

print(patient.head())
print(patient.columns)
print(food.columns)

print("\nFood Columns:")
print(food.columns.tolist())
print("\nHealth Goals:")
print(patient["Health_goal"].unique())

print("\nDiet Preferences:")
print(patient["Diet_preference"].unique())

print("\nFood Nutrients:")
print(food["nutritions"].unique())

print("\nMissing values in Food Dataset:")
print(food.isnull().sum())

print("\nMissing values in Patient Dataset:")
print(patient.isnull().sum())

print("\nDuplicate rows in Food Dataset:")
print(food.duplicated().sum())

print("\nDuplicate rows in Patient Dataset:")
print(patient.duplicated().sum())

print("\nGender values:")
print(patient["Gender"].unique())

print("\nActivity levels:")
print(patient["Activity_level"].unique())

print("\nHealth goals:")
print(patient["Health_goal"].unique())

print("\nDiet preferences:")
print(patient["Diet_preference"].unique())
print("\nNumeric Data Check:")

print("\nAge:")
print(patient["Age"].describe())

print("\nHeight:")
print(patient["Height_cm"].describe())

print("\nWeight:")
print(patient["Weight_level"].describe())
print("\nFood Data Types:")
print(food.dtypes)

print("\nPatient Data Types:")
print(patient.dtypes)

print("\nFood Data Types:")
print(food.dtypes)

print("\nPatient Data Types:")
print(patient.dtypes)
# Create clean copies
food_clean = food.copy()
patient_clean = patient.copy()

print("\nClean copies created successfully")
print("Food shape:", food_clean.shape)
print("Patient shape:", patient_clean.shape)
print("\nInvalid Age:")
print(patient_clean[patient_clean["Age"] <= 0])

print("\nInvalid Height:")
print(patient_clean[patient_clean["Height_cm"] <= 0])

print("\nInvalid Weight:")
print(patient_clean[patient_clean["Weight_level"] <= 0])
print("\nInvalid Food Nutrition Values:")

nutrition_columns = [
    "calories_kcal_per_serving",
    "carbs_g",
    "protein_g",
    "fat_g",
    "sugar_g",
    "fiber_g"
]

for column in nutrition_columns:
    print(f"\nInvalid {column}:")
    print(food_clean[food_clean[column] < 0])

    print("\n--- Food Categorical Values ---")

print("\nFood Categories:")
print(food_clean["category"].unique())

print("\nMeal Types:")
print(food_clean["meal_type"].unique())


# 7. Food Boolean Columns
print("\n--- Food Boolean Values ---")

print("Diabetic Friendly:")
print(food_clean["diabetic_friendly"].unique())

print("High Protein:")
print(food_clean["high_protein"].unique())

print("Is Healthy:")
print(food_clean["is_healthy"].unique())


print("\n========== VALIDATION COMPLETED ==========")


from sklearn.preprocessing import LabelEncoder

# Create encoder
encoder = LabelEncoder()

# Encode patient categorical columns
patient_clean["Gender_encoded"] = encoder.fit_transform(patient_clean["Gender"])
patient_clean["Activity_encoded"] = encoder.fit_transform(patient_clean["Activity_level"])
patient_clean["Health_goal_encoded"] = encoder.fit_transform(patient_clean["Health_goal"])
patient_clean["Diet_encoded"] = encoder.fit_transform(patient_clean["Diet_preference"])

print("\nEncoded Patient Data:")
print(patient_clean.head())