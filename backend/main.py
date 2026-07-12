import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import uvicorn
import pandas as pd
import numpy as np
import io
import sqlite3
import bcrypt
import yfinance as yf  # 🟢 El library el gdeda beta3t el Live Data wel News
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 1. Security & DB Setup ---

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create users table on startup
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                     username TEXT UNIQUE, 
                     password TEXT)''')
    conn.commit()
    conn.close()

init_db()

class UserAuth(BaseModel):
    username: str
    password: str

class TickerRequest(BaseModel):
    ticker: str

# --- 2. Configuration & Global Variables ---
app = FastAPI(title="Stock Prediction API with Auth & Live Data")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
scaler = None
latest_data_df = None
all_predictions_df = None
TIME_STEP = 60

# --- 3. Helper Functions ---
def create_dataset(dataset, time_step=60):
    X, Y = [], []
    for i in range(len(dataset) - time_step - 1):
        X.append(dataset[i:(i + time_step), 0])
        Y.append(dataset[i + time_step, 0])
    return np.array(X), np.array(Y)

def calculate_mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero_mask = y_true != 0
    if np.sum(non_zero_mask) == 0: return 0.0
    return np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100

# 🟢 Function gdeda 3ashan n-wa7ad el training (tzbat m3 el CSV wel Live Data)
def train_model_logic(df):
    global model, scaler, latest_data_df, all_predictions_df
    
    latest_data_df = df
    data = df[['close']].values
    current_scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = current_scaler.fit_transform(data)

    X, Y = create_dataset(scaled_data, TIME_STEP)
    if len(X) == 0:
        raise ValueError("Not enough data to train. Need at least 61 rows.")

    X = X.reshape(X.shape[0], X.shape[1], 1)

    current_model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(TIME_STEP, 1)),
        Dropout(0.2),
        LSTM(50, return_sequences=False),
        Dropout(0.2),
        Dense(25, activation='relu'),
        Dense(1)
    ])
    current_model.compile(optimizer='adam', loss='mean_squared_error')
    
    epochs = 30
    batch_size = 32
    history = current_model.fit(X, Y, epochs=epochs, batch_size=batch_size, verbose=1, validation_split=0.2)
    
    all_predictions_scaled = current_model.predict(X)
    all_predictions = current_scaler.inverse_transform(all_predictions_scaled)
    real_prices = current_scaler.inverse_transform(Y.reshape(-1, 1))

    chart_df = latest_data_df.iloc[TIME_STEP+1:].copy()
    chart_df['predicted'] = all_predictions
    chart_df['real'] = real_prices
    all_predictions_df = chart_df

    model = current_model
    scaler = current_scaler

    return real_prices, all_predictions, history.history

# --- 4. Auth Endpoints ---

@app.post("/register")
async def register(user: UserAuth):
    conn = get_db_connection()
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(user.password.encode('utf-8'), salt)
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user.username, hashed_pwd.decode('utf-8')))
        conn.commit()
        return {"message": "User registered successfully"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()

@app.post("/login")
async def login(user: UserAuth):
    conn = get_db_connection()
    db_user = conn.execute("SELECT * FROM users WHERE username = ?", (user.username,)).fetchone()
    conn.close()
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "username": user.username}

# --- 5. Prediction & Live Data Endpoints ---

@app.get("/")
def read_root():
    return {"message": "API is running. Please Login to continue."}

# 🟢 El Endpoint el Adeem (law 3ayez trfa3 CSV)
@app.post("/upload_and_train")
async def upload_and_train(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        df.rename(columns=lambda x: x.strip().lower(), inplace=True)
        
        if 'date' not in df.columns or 'close' not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must have 'date' and 'close' columns.")

        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df = df.dropna(subset=['close'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        real_prices, all_predictions, history = train_model_logic(df)

        mae = mean_absolute_error(real_prices, all_predictions)
        rmse = np.sqrt(mean_squared_error(real_prices, all_predictions))
        mape = calculate_mape(real_prices, all_predictions)

        return {
            "message": "Model trained successfully from CSV", 
            "metrics": {"mae": f"${mae:.2f}", "rmse": f"${rmse:.2f}", "mape": f"{mape:.2f}%"},
            "training_history": {"loss": [float(l) for l in history['loss']], "val_loss": [float(l) for l in history['val_loss']]}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🟢 El Endpoint el Gded (Bygeeb data live mn Yahoo Finance)
@app.post("/train_ticker")
async def train_ticker(req: TickerRequest):
    try:
        print(f"Fetching Live Data for {req.ticker}...")
        stock = yf.Ticker(req.ticker)
        df = stock.history(period="2y") # Bygeeb a5er sanateen
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Ticker not found or no data available.")
            
        df = df.reset_index()
        df.rename(columns={'Date': 'date', 'Close': 'close'}, inplace=True)
        df['date'] = df['date'].dt.tz_localize(None) # By-zabat wa2t el API
        df = df.sort_values('date').reset_index(drop=True)

        real_prices, all_predictions, history = train_model_logic(df)
        
        mae = mean_absolute_error(real_prices, all_predictions)
        rmse = np.sqrt(mean_squared_error(real_prices, all_predictions))
        mape = calculate_mape(real_prices, all_predictions)

        return {
            "message": f"Model trained successfully on Live {req.ticker} data!", 
            "metrics": {"mae": f"${mae:.2f}", "rmse": f"${rmse:.2f}", "mape": f"{mape:.2f}%"},
            "training_history": {"loss": [float(l) for l in history['loss']], "val_loss": [float(l) for l in history['val_loss']]}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🟢 Endpoint el News (Updated format for yfinance)
@app.get("/news/{ticker}")
def get_news(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        news_data = stock.news
        cleaned_news = []
        for item in news_data[:4]: # Byrg3 a5er 4 a5bar
            # yfinance update: the data is sometimes nested inside 'content'
            content = item.get("content", item) 
            cleaned_news.append({
                "title": content.get("title", "News Article Unavailable"),
                "publisher": content.get("provider", {}).get("displayName", content.get("publisher", "Yahoo Finance")),
                "link": content.get("clickThroughUrl", content.get("link", "#"))
            })
        return {"news": cleaned_news}
    except Exception as e:
        print(f"Error fetching news: {e}")
        return {"news": []}

@app.get("/all_predictions")
def get_all_predictions():
    if all_predictions_df is None: return []
    df_json = all_predictions_df.copy()
    df_json['date'] = df_json['date'].dt.strftime('%Y-%m-%d')
    return df_json[['date', 'real', 'predicted']].to_dict('records')

@app.get("/predict_next_day")
def predict_next_day():
    if not model or not scaler or latest_data_df is None:
        raise HTTPException(status_code=503, detail="Model is not trained. Please upload a dataset and train first.")
    try:
        data = latest_data_df[['close']].values
        last_60_days = data[-TIME_STEP:]
        last_60_days_scaled = scaler.transform(last_60_days)
        X_test = np.array([last_60_days_scaled])
        
        predicted_price_scaled = model.predict(X_test)
        predicted_price = scaler.inverse_transform(predicted_price_scaled)

        return {"prediction": float(predicted_price[0][0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")

if __name__ == "__main__":
    print("Starting API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)