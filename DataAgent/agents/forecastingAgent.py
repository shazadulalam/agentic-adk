import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Time series models - optional dependencies
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    ARIMA = None
    seasonal_decompose = None
    adfuller = None

import joblib
import os

# Prophet - optional dependency
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    Prophet = None

# Deep learning for time series
try:
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

from config import *

class ForecastingAgent:
    """
    Agent for time series forecasting using multiple models:
    - ARIMA
    - Prophet
    - LSTM (if TensorFlow available)
    """
    
    def __init__(self):
        self.models_dir = MODELS_DIR
        os.makedirs(self.models_dir, exist_ok=True)
    
    def prepare_time_series(self, df: pd.DataFrame, date_col: str, value_col: str, freq: str = 'D') -> pd.Series:
        """Prepare time series data from dataframe"""
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        ts = df.set_index(date_col)[value_col]
        ts = ts.asfreq(freq).ffill()
        ts = ts.bfill()
        return ts
    
    def check_stationarity(self, ts: pd.Series) -> dict:
        """Check if time series is stationary using Augmented Dickey-Fuller test"""
        if not STATSMODELS_AVAILABLE:
            return {
                'error': 'statsmodels is not installed. Install it with: pip install statsmodels'
            }
        result = adfuller(ts.dropna())
        return {
            'adf_statistic': result[0],
            'p_value': result[1],
            'is_stationary': result[1] < 0.05
        }
    
    def make_stationary(self, ts: pd.Series) -> pd.Series:
        """Make time series stationary using differencing"""
        ts_diff = ts.diff().dropna()
        return ts_diff
    
    def forecast_arima(self, ts: pd.Series, forecast_periods: int = 30, order: tuple = None) -> dict:
        """
        Forecast using ARIMA model
        Returns: dict with forecast, confidence intervals, and model
        """
        if not STATSMODELS_AVAILABLE:
            return {
                'error': 'statsmodels is not installed. Install it with: pip install statsmodels'
            }
        
        # Auto-determine order if not provided
        if order is None:
            # Simple auto-arima approximation
            order = self._auto_arima_order(ts)
        
        model = ARIMA(ts, order=order)
        fitted_model = model.fit()
        
        # Forecast
        forecast = fitted_model.forecast(steps=forecast_periods)
        conf_int = fitted_model.get_forecast(steps=forecast_periods).conf_int()
        
        # Save model
        model_path = os.path.join(self.models_dir, 'arima_model.pkl')
        joblib.dump(fitted_model, model_path)
        
        return {
            'forecast': forecast,
            'confidence_intervals': conf_int,
            'model': fitted_model,
            'model_path': model_path,
            'aic': fitted_model.aic
        }
    
    def _auto_arima_order(self, ts: pd.Series, max_p: int = 3, max_d: int = 2, max_q: int = 3) -> tuple:
        """Simple auto-arima order selection"""
        if not STATSMODELS_AVAILABLE:
            return (1, 1, 1)  # Default order
        
        best_aic = np.inf
        best_order = (1, 1, 1)
        
        for p in range(max_p + 1):
            for d in range(max_d + 1):
                for q in range(max_q + 1):
                    try:
                        model = ARIMA(ts, order=(p, d, q))
                        fitted = model.fit()
                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        return best_order
    
    def forecast_prophet(self, df: pd.DataFrame, date_col: str, value_col: str, 
                        forecast_periods: int = 30, seasonality: dict = None) -> dict:
        """
        Forecast using Facebook Prophet
        Returns: dict with forecast dataframe and model
        """
        if not PROPHET_AVAILABLE:
            return {
                'error': 'Prophet is not installed. Install it with: pip install prophet'
            }
        
        # Prepare data for Prophet
        prophet_df = df[[date_col, value_col]].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        prophet_df = prophet_df.sort_values('ds')
        
        # Initialize Prophet model
        if seasonality:
            model = Prophet(**seasonality)
        else:
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False
            )
        
        # Fit model
        model.fit(prophet_df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=forecast_periods, freq='D')
        
        # Forecast
        forecast_df = model.predict(future)
        
        # Save model
        model_path = os.path.join(self.models_dir, 'prophet_model.pkl')
        joblib.dump(model, model_path)
        
        return {
            'forecast': forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
            'model': model,
            'model_path': model_path,
            'components': model.plot_components(forecast_df) if hasattr(model, 'plot_components') else None
        }
    
    def forecast_lstm(self, ts: pd.Series, forecast_periods: int = 30, 
                     lookback: int = 60, epochs: int = 50) -> dict:
        """
        Forecast using LSTM neural network
        Returns: dict with forecast and model
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow is required for LSTM forecasting")
        
        # Normalize data
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        ts_scaled = scaler.fit_transform(ts.values.reshape(-1, 1))
        
        # Create sequences
        X, y = [], []
        for i in range(lookback, len(ts_scaled)):
            X.append(ts_scaled[i-lookback:i, 0])
            y.append(ts_scaled[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Build LSTM model
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=True),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1)
        ])
        
        model.compile(optimizer='adam', loss='mse')
        
        # Train model
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
        model.fit(X_train, y_train, epochs=epochs, batch_size=32, 
                 validation_data=(X_test, y_test), callbacks=[early_stop], verbose=0)
        
        # Forecast
        last_sequence = ts_scaled[-lookback:].reshape(1, lookback, 1)
        forecasts = []
        current_seq = last_sequence.copy()
        
        for _ in range(forecast_periods):
            next_pred = model.predict(current_seq, verbose=0)
            forecasts.append(next_pred[0, 0])
            # Update sequence
            current_seq = np.append(current_seq[:, 1:, :], next_pred.reshape(1, 1, 1), axis=1)
        
        # Inverse transform
        forecasts = scaler.inverse_transform(np.array(forecasts).reshape(-1, 1)).flatten()
        
        # Save model and scaler
        model_path = os.path.join(self.models_dir, 'lstm_model.h5')
        scaler_path = os.path.join(self.models_dir, 'lstm_scaler.pkl')
        model.save(model_path)
        joblib.dump(scaler, scaler_path)
        
        return {
            'forecast': forecasts,
            'model': model,
            'model_path': model_path,
            'scaler_path': scaler_path,
            'lookback': lookback
        }
    
    def compare_forecasts(self, ts: pd.Series, forecast_periods: int = 30) -> dict:
        """Compare multiple forecasting models"""
        results = {}
        
        # ARIMA
        try:
            arima_result = self.forecast_arima(ts, forecast_periods)
            results['arima'] = arima_result
        except Exception as e:
            results['arima'] = {'error': str(e)}
        
        # Prophet (requires dataframe)
        try:
            df = pd.DataFrame({
                'date': ts.index,
                'value': ts.values
            })
            prophet_result = self.forecast_prophet(df, 'date', 'value', forecast_periods)
            results['prophet'] = prophet_result
        except Exception as e:
            results['prophet'] = {'error': str(e)}
        
        # LSTM
        if TENSORFLOW_AVAILABLE:
            try:
                lstm_result = self.forecast_lstm(ts, forecast_periods)
                results['lstm'] = lstm_result
            except Exception as e:
                results['lstm'] = {'error': str(e)}
        
        return results
    
    def decompose_time_series(self, ts: pd.Series, model: str = 'additive', period: int = None) -> dict:
        """Decompose time series into trend, seasonal, and residual components"""
        if not STATSMODELS_AVAILABLE:
            return {
                'error': 'statsmodels is not installed. Install it with: pip install statsmodels'
            }
        
        if period is None:
            # Auto-detect period
            if len(ts) > 365:
                period = 365  # yearly
            elif len(ts) > 30:
                period = 30  # monthly
            else:
                period = 7  # weekly
        
        decomposition = seasonal_decompose(ts, model=model, period=period)
        
        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'observed': decomposition.observed
        }
