import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


# Load the data from excel file
data = pd.read_excel('eth_name_2.xlsx', engine='openpyxl')

# Split the data into input features (name) and target variable (class)
X = data['name']
y = data['class']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(X_train)
# Convert the text data into numerical features using CountVectorizer
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Build a logistic regression model
model = LogisticRegression()
model.fit(X_train_vectorized, y_train)

# Evaluate the model
accuracy = model.score(X_test_vectorized, y_test)
print("Model Accuracy:", accuracy)

# # Predict the class of a new name
# new_name = "נגסתי"
# new_name_vectorized = vectorizer.transform([new_name])
# prediction = model.predict(new_name_vectorized)
#
# print("Prediction for", new_name, ":", prediction[0])