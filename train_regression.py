from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from feature_builder import fetch_features
import numpy as np

df = fetch_features()

X = df[['query_length', 'response_time']]
y = df['confidence_score']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)

preds = model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, preds))
mae = mean_absolute_error(y_test, preds)

print("Regression RMSE:", rmse)
print("Regression MAE:", mae)
