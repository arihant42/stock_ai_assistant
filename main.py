import pandas as pd
import numpy as np
import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from flask import Flask, request, jsonify
import os
import datetime

# --------------------------------------------
# CONFIG
# --------------------------------------------
SYMBOL = "RELIANCE.NS"
START_DATE = "2020-01-01"
END_DATE = datetime.date.today().strftime("%Y-%m-%d")

# --------------------------------------------
# FETCH STOCK DATA
# --------------------------------------------
def get_stock_data(symbol, start_date, end_date):
    try:
        df = yf.download(symbol, start=start_date, end=end_date)
        if df.empty:
            print(f"[❌] No data for {symbol}")
            return None
        return df
    except Exception as e:
        print(f"[❌] Failed to fetch data for {symbol}: {e}")
        return None

stock_data = get_stock_data(SYMBOL, START_DATE, END_DATE)
if stock_data is None:
    exit()

# --------------------------------------------
# FEATURE ENGINEERING
# --------------------------------------------
stock_data['SMA_50'] = stock_data['Close'].rolling(window=50).mean()
stock_data['SMA_200'] = stock_data['Close'].rolling(window=200).mean()
stock_data['RSI'] = 100 - (100 / (1 + stock_data['Close'].pct_change().rolling(14).mean() / stock_data['Close'].pct_change().rolling(14).std()))
stock_data['MACD'] = stock_data['Close'].ewm(span=12, adjust=False).mean() - stock_data['Close'].ewm(span=26, adjust=False).mean()
stock_data['Signal_Line'] = stock_data['MACD'].ewm(span=9, adjust=False).mean()
stock_data = stock_data.dropna()

features = ['Open', 'High', 'Low', 'Close', 'Volume', 'SMA_50', 'SMA_200', 'RSI', 'MACD', 'Signal_Line']
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(stock_data[features])

X = scaled_data[:-1]
y = scaled_data[1:, 3]  # next day's close
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --------------------------------------------
# RANDOM FOREST MODEL
# --------------------------------------------
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
predictions = model.predict(X_test)

# --------------------------------------------
# DEEP LEARNING LSTM MODEL
# --------------------------------------------
nn_model = keras.Sequential([
    keras.layers.Input(shape=(X_train.shape[1],)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dense(1)
])
nn_model.compile(optimizer='adam', loss='mse')
nn_model.fit(X_train, y_train, epochs=50, batch_size=16, verbose=1)

# --------------------------------------------
# PREDICT FUTURE
# --------------------------------------------
def predict_future_price(model, latest_data):
    scaled = scaler.transform([latest_data])
    prediction = model.predict(scaled)
    inversed = scaler.inverse_transform([[0, 0, 0, prediction[0], 0, 0, 0, 0, 0, 0]])
    return inversed[0][3]

latest_data = stock_data[features].iloc[-1].values
predicted_price = predict_future_price(nn_model, latest_data)
print(f"📈 Predicted Next Close for {SYMBOL}: ₹{round(predicted_price, 2)}")

# --------------------------------------------
# VISUALIZE
# --------------------------------------------
plt.figure(figsize=(10, 5))
sns.lineplot(x=stock_data.index, y=stock_data['Close'], label='Actual Close')
sns.lineplot(x=stock_data.index[-len(y_test):], y=scaler.inverse_transform([[0, 0, 0, p, 0, 0, 0, 0, 0, 0]])[:,3] for p in predictions], label='RF Predicted')
plt.title(f"{SYMBOL} - Actual vs Predicted")
plt.legend()
plt.show()

# --------------------------------------------
# FLASK API
# --------------------------------------------
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json['features']
    prediction = predict_future_price(nn_model, data)
    return jsonify({"predicted_price": round(prediction, 2)})

if __name__ == '__main__':
    app.run(debug=True)
