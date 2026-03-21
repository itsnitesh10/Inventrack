import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from app.models import StockMovement
from app import db


def get_movement_data(product_id):
    movements = (
        StockMovement.query
        .filter_by(product_id=product_id, movement_type='out')
        .order_by(StockMovement.created_at)
        .all()
    )
    if not movements:
        return None

    records = [{'date': m.created_at.date(), 'quantity': m.quantity} for m in movements]
    df = pd.DataFrame(records)
    df = df.groupby('date')['quantity'].sum().reset_index()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    full_range = pd.date_range(df['date'].min(), df['date'].max(), freq='D')
    df = df.set_index('date').reindex(full_range, fill_value=0).reset_index()
    df.columns = ['date', 'quantity']
    return df


def build_features(df):
    df = df.copy()
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    df['day_index'] = (df['date'] - df['date'].min()).dt.days

    for lag in [1, 3, 7]:
        df[f'lag_{lag}'] = df['quantity'].shift(lag).fillna(0)
    df['rolling_mean_7'] = df['quantity'].rolling(7, min_periods=1).mean()
    df['rolling_std_7'] = df['quantity'].rolling(7, min_periods=1).std().fillna(0)

    return df


def forecast_product(product_id, periods=30):
    df = get_movement_data(product_id)
    if df is None or len(df) < 5:
        return {
            'status': 'insufficient_data',
            'message': 'Need at least 5 stock-out records to forecast.',
            'product_id': product_id
        }

    df = build_features(df)
    feature_cols = ['day_of_week', 'day_of_month', 'month', 'week_of_year',
                    'day_index', 'lag_1', 'lag_3', 'lag_7',
                    'rolling_mean_7', 'rolling_std_7']

    X = df[feature_cols].values
    y = df['quantity'].values

    split = max(1, int(len(df) * 0.8))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # Train two models
    lr = LinearRegression()
    lr.fit(X_train, y_train)

    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    # Evaluate
    if len(X_test) > 0:
        lr_preds = np.clip(lr.predict(X_test), 0, None)
        rf_preds = np.clip(rf.predict(X_test), 0, None)
        lr_mae = round(mean_absolute_error(y_test, lr_preds), 2)
        rf_mae = round(mean_absolute_error(y_test, rf_preds), 2)
    else:
        lr_mae = rf_mae = None

    # Best model
    best_model = rf if (rf_mae is not None and (lr_mae is None or rf_mae <= lr_mae)) else lr
    best_name = 'Random Forest' if best_model is rf else 'Linear Regression'

    # Future forecast
    last_date = df['date'].max()
    future_dates = [last_date + timedelta(days=i+1) for i in range(periods)]
    last_quantities = list(df['quantity'].values[-7:])

    future_preds = []
    for i, fd in enumerate(future_dates):
        row = {
            'date': fd,
            'day_of_week': fd.dayofweek,
            'day_of_month': fd.day,
            'month': fd.month,
            'week_of_year': fd.isocalendar()[1],
            'day_index': (fd - df['date'].min()).days,
            'lag_1': last_quantities[-1] if last_quantities else 0,
            'lag_3': last_quantities[-3] if len(last_quantities) >= 3 else 0,
            'lag_7': last_quantities[-7] if len(last_quantities) >= 7 else 0,
            'rolling_mean_7': np.mean(last_quantities[-7:]) if last_quantities else 0,
            'rolling_std_7': np.std(last_quantities[-7:]) if len(last_quantities) >= 2 else 0,
        }
        feat = np.array([[row[c] for c in feature_cols]])
        pred = float(np.clip(best_model.predict(feat)[0], 0, None))
        future_preds.append(round(pred, 1))
        last_quantities.append(pred)

    # Historical (last 60 days for chart)
    hist = df.tail(60)

    return {
        'status': 'ok',
        'product_id': product_id,
        'best_model': best_name,
        'lr_mae': lr_mae,
        'rf_mae': rf_mae,
        'total_history_days': len(df),
        'avg_daily_demand': round(float(df['quantity'].mean()), 2),
        'max_daily_demand': int(df['quantity'].max()),
        'forecast_periods': periods,
        'forecast_total': round(sum(future_preds), 1),
        'forecast_daily_avg': round(sum(future_preds) / periods, 2),
        'historical_dates': [str(d.date()) for d in hist['date']],
        'historical_values': [float(v) for v in hist['quantity']],
        'forecast_dates': [str(d.date()) for d in future_dates],
        'forecast_values': future_preds,
    }


def get_forecast_summary(product_id):
    result = forecast_product(product_id, periods=30)
    if result.get('status') != 'ok':
        return None
    return {
        'avg_daily': result['avg_daily_demand'],
        'forecast_30d': result['forecast_total'],
        'best_model': result['best_model'],
        'rf_mae': result['rf_mae'],
    }