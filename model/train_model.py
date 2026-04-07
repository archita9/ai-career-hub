# STEP 1: Import tools
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import pickle

# STEP 2: Load dataset
data = pd.read_csv("../data/placement_data.csv")

# STEP 3: Separate inputs (X) and output (y)
X = data.drop("placed", axis=1)
y = data["placed"]

# STEP 4: Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# STEP 5: Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# STEP 6: Save trained model
with open("placement_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("✅ Model trained and saved successfully")
