# Inventrack

## AI-Powered Inventory Management & Demand Forecasting System

Inventrack is a full-stack inventory management system designed to help businesses manage products, stock levels, purchase orders, sales data, and inventory movements while using machine learning to forecast future product demand.

The system combines traditional inventory management with an ML-based demand forecasting pipeline that evaluates multiple regression models and automatically selects the best-performing model for generating future demand predictions.

---

## Overview

Managing inventory manually can make it difficult to identify upcoming stock shortages and determine how much inventory should be reordered.

Inventrack addresses this by combining:

* Inventory and product management
* Stock movement tracking
* Purchase order management
* CSV/XLSX data ingestion
* Historical sales analysis
* Machine learning-based demand forecasting
* Stockout prediction
* Reorder quantity recommendations
* Low-stock and out-of-stock notifications

The goal is to provide a single platform where inventory data can be managed and historical demand can be used to support inventory planning decisions.

---

## Key Features

### 1. User Authentication

* User registration and login
* Secure password hashing using Werkzeug
* Session-based authentication using Flask-Login
* User roles such as staff
* Protected application routes

### 2. Product Management

* Add, edit, view, and manage products
* SKU-based product identification
* Product categories
* Product descriptions
* Unit pricing
* Configurable reorder levels
* Active/inactive product status

### 3. Inventory Management

* Track current stock levels
* Stock-in and stock-out operations
* Manual stock adjustments
* Stock movement history
* Automatic low-stock detection
* Out-of-stock detection
* Product-level inventory information

### 4. Purchase Order Management

* Create purchase orders
* Add multiple products to an order
* Track suppliers
* Track order status
* Calculate order total cost
* Mark orders as received
* Record order creation and receiving dates
* Automatically update inventory when orders are received

### 5. Data Import & Ingestion

Inventrack supports importing inventory and sales data from:

* CSV files
* XLSX files

The ingestion pipeline performs:

* Column normalization
* Column alias handling
* Required-column validation
* Date parsing
* Numeric type conversion
* Negative quantity handling
* Missing-value handling
* SKU validation
* Product-name validation
* Data cleaning and warnings

Supported required fields include:

```text
product_name
sku
date
quantity_sold
```

Optional fields include:

```text
category
unit_price
reorder_level
stock_quantity
description
```

### 6. Demand Forecasting

The ML module uses historical sales data to predict future product demand.

The forecasting pipeline:

1. Processes historical sales data
2. Creates time-series features
3. Splits data into training and testing sets
4. Trains multiple regression models
5. Evaluates model performance
6. Selects the best-performing model
7. Generates future demand predictions

The system can generate forecasts for future periods, with the application primarily using a **30-day forecasting horizon**.

### 7. Machine Learning Models

The main ML training pipeline evaluates:

* Linear Regression
* Random Forest Regressor
* XGBoost Regressor

#### Linear Regression

Used as a baseline model for comparing forecasting performance.

#### Random Forest

Uses an ensemble of decision trees to capture nonlinear relationships in historical demand data.

#### XGBoost

Uses gradient-boosted decision trees and is evaluated alongside the other models to determine whether it provides better forecasting performance.

### 8. Feature Engineering

The forecasting pipeline generates time-based and historical-demand features including:

* Day of week
* Day of month
* Month
* Week of year
* Day index
* 1-day lag
* 3-day lag
* 7-day lag
* 14-day lag
* 30-day lag
* 7-day rolling average
* 14-day rolling average
* 30-day rolling average
* 7-day rolling standard deviation

These features allow the models to learn patterns from historical demand and temporal behavior.

### 9. Automatic Model Selection

Instead of relying on a single forecasting model, Inventrack evaluates the available models using:

* MAE — Mean Absolute Error
* RMSE — Root Mean Squared Error
* MAPE — Mean Absolute Percentage Error

The system automatically selects the model with the lowest MAPE score. If MAPE cannot distinguish between models, MAE can be used as a fallback.

This allows the forecasting pipeline to choose the model that performs best on the available historical data.

### 10. Inventory Decision Support

The forecasting output is connected to inventory planning.

Based on predicted demand, Inventrack can calculate:

* Average daily predicted demand
* Total forecasted demand
* Estimated stockout date
* Estimated days until stockout
* Suggested reorder quantity

The reorder recommendation is calculated using approximately:

```text
30-day forecast demand × 1.20
```

This provides a 30-day demand cover with an additional 20% buffer.

### 11. Notifications

The system provides notifications for important inventory events such as:

* Low-stock products
* Out-of-stock products
* Purchase orders being created
* Purchase orders being received
* Purchase orders being cancelled

Notifications are exposed through application API endpoints and displayed within the application.

---

## Machine Learning Workflow

```text
Historical Sales Data
        |
        v
Data Ingestion
        |
        v
Data Validation & Cleaning
        |
        v
Time-Series Construction
        |
        v
Feature Engineering
        |
        +-------------------+
        |                   |
        v                   v
Linear Regression     Random Forest
        |                   |
        +---------+---------+
                  |
                  v
              XGBoost
                  |
                  v
        Model Evaluation
        MAE / RMSE / MAPE
                  |
                  v
       Best Model Selection
                  |
                  v
        Future Demand Forecast
                  |
                  v
     Inventory Decision Support
        /                 \
       v                   v
 Stockout Prediction   Reorder Quantity
```

---

## System Architecture

```text
                         Inventrack
                             |
             +---------------+---------------+
             |                               |
             v                               v
        Web Interface                    Flask Backend
       HTML / CSS / JS                       |
                                             |
             +---------------+---------------+
             |               |               |
             v               v               v
        Products          Inventory       Orders
             |               |               |
             +---------------+---------------+
                             |
                             v
                       Data Ingestion
                       CSV / XLSX
                             |
                             v
                    Data Preprocessing
                             |
                             v
                    ML Forecasting
                             |
          +------------------+------------------+
          |                  |                  |
          v                  v                  v
     Linear Regression   Random Forest       XGBoost
          |                  |                  |
          +------------------+------------------+
                             |
                             v
                     Model Evaluation
                       MAE / RMSE / MAPE
                             |
                             v
                     Demand Prediction
                             |
                             v
                  Inventory Recommendations
```

---

## Technology Stack

### Backend

* Python
* Flask
* Flask-SQLAlchemy
* Flask-Login
* Werkzeug

### Database

* SQLite
* SQLAlchemy ORM

### Machine Learning & Data Processing

* Scikit-learn
* XGBoost
* Pandas
* NumPy
* SciPy

### Data Import

* OpenPyXL
* Pandas

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### Development

* Python
* VS Code
* Git
* GitHub

---

## Project Structure

```text
inventrack_v4/
│
├── run.py
├── requirements.txt
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── notifications.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── products/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── stock/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── orders/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── forecasting/
│   │   ├── __init__.py
│   │   ├── model.py
│   │   └── routes.py
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── trainer.py
│   │   └── predictor.py
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── cleaner.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   └── routes.py
│   │
│   ├── dashboard/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   └── templates/
│       ├── auth/
│       ├── dashboard/
│       ├── products/
│       ├── stock/
│       ├── orders/
│       ├── forecasting/
│       └── ingestion/
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
```

---

## Database Design

The application uses SQLite with SQLAlchemy ORM.

### Main Entities

#### Users

Stores application users and authentication information.

```text
id
username
email
password_hash
role
created_at
```

#### Products

Stores product information.

```text
id
name
sku
description
unit_price
reorder_level
category_id
created_at
is_active
```

#### Stock

Stores the current inventory level for each product.

```text
id
product_id
quantity
last_updated
```

#### Orders

Stores purchase order information.

```text
id
order_number
supplier
status
created_by
created_at
received_at
notes
```

#### Order Items

Stores products and quantities belonging to purchase orders.

```text
id
order_id
product_id
quantity
unit_price
```

#### Stock Movements

Tracks inventory movement history.

```text
id
product_id
movement_type
quantity
reference
created_by
created_at
notes
```

#### Sales History

Stores historical product-level sales information used for forecasting.

```text
id
product_id
date
quantity_sold
stock_qty
uploaded_at
```

#### Forecast Results

Stores generated ML forecast results.

```text
id
product_id
model_used
forecast_days
forecast_date
predicted_qty
mae
rmse
mape
generated_at
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/inventrack.git
cd inventrack
```

Replace `<your-username>` with your GitHub username.

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python run.py
```

The Flask development server will start locally.

Open:

```text
http://127.0.0.1:5000
```

The SQLite database is created automatically when the Flask application initializes.

---

## Requirements

The project uses the following major dependencies:

```text
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.0.1
scikit-learn==1.4.0
pandas==2.1.4
numpy==1.26.3
openpyxl==3.1.2
xgboost==2.0.3
scipy==1.12.0
```

Python 3.10+ is recommended.

---

## Forecasting Data Format

For demand forecasting through uploaded data, the system expects at least:

```csv
product_name,sku,date,quantity_sold
Laptop,LP001,2026-01-01,5
Laptop,LP001,2026-01-02,7
Laptop,LP001,2026-01-03,4
```

Additional optional fields can be provided:

```csv
product_name,sku,date,quantity_sold,category,unit_price,reorder_level,stock_quantity,description
```

The ingestion system also supports common column aliases such as:

```text
product → product_name
product_sku → sku
sale_date → date
qty_sold → quantity_sold
sales → quantity_sold
units_sold → quantity_sold
stock → stock_quantity
price → unit_price
min_stock → reorder_level
```

---

## Data Preprocessing

Before the forecasting model is trained, the system performs several preprocessing operations:

1. Parse and normalize dates
2. Convert numerical columns to appropriate data types
3. Handle missing values
4. Handle negative quantities
5. Validate SKU and product names
6. Fill missing dates in time-series data
7. Detect and replace extreme outliers using the IQR method
8. Generate rolling statistics
9. Generate lag-based features

This helps provide cleaner time-series data to the forecasting models.

---

## Model Evaluation

Inventrack evaluates the forecasting models using three primary metrics.

### MAE

Mean Absolute Error measures the average absolute difference between actual and predicted demand.

```text
MAE = average(|actual - predicted|)
```

Lower MAE indicates better performance.

### RMSE

Root Mean Squared Error penalizes larger prediction errors more heavily.

```text
RMSE = sqrt(mean((actual - predicted)²))
```

Lower RMSE indicates better performance.

### MAPE

Mean Absolute Percentage Error measures prediction error as a percentage.

```text
MAPE = mean(|actual - predicted| / actual) × 100
```

Lower MAPE indicates better forecasting performance.

---

## Inventory Intelligence

The ML predictions are used to generate practical inventory insights.

### Stockout Prediction

The system cumulatively adds predicted daily demand against current stock to estimate when inventory may reach zero.

```text
Current Stock
      |
      v
Predicted Daily Demand
      |
      v
Cumulative Forecast Demand
      |
      v
Estimated Stockout Date
```

### Reorder Recommendation

The system estimates reorder quantity using predicted average daily demand:

```text
Reorder Quantity =
Average Daily Forecast × 30 × 1.20
```

The additional 20% provides a demand buffer.

---

## Security

The application includes basic authentication and password security features:

* Password hashing using Werkzeug
* Login session management using Flask-Login
* Protected application routes
* Unique usernames and email addresses

For production deployment, additional security configuration would be required, including:

* Environment-based secret keys
* Production WSGI server
* HTTPS
* CSRF protection
* Production database
* Secure cookie configuration
* Proper environment configuration

---

## Current Limitations

Inventrack is primarily a project/development implementation and has several areas that could be improved for production use:

* SQLite is used as the database
* Notifications are stored in memory and reset when the server restarts
* Forecasting quality depends on the amount and quality of historical sales data
* At least a minimum amount of historical data is required for ML forecasting
* The application currently runs using Flask's development server
* Production authentication and security hardening would be required before deployment at scale

---

## Future Improvements

Potential future improvements include:

* PostgreSQL/MySQL production database
* Cloud deployment
* Redis-based notification system
* Background forecasting jobs using Celery
* More advanced time-series models
* Seasonal forecasting
* Hyperparameter optimization
* Model versioning
* Automated model retraining
* Supplier performance analytics
* Multi-warehouse inventory management
* Role-based access control
* Advanced analytics dashboard
* Real-time inventory synchronization
* Demand anomaly detection
* Email/SMS inventory alerts

---

## Use Cases

Inventrack can be adapted for:

* Retail stores
* E-commerce businesses
* Warehouses
* Small and medium-sized businesses
* Product distributors
* Inventory teams
* Supply-chain operations

---

## What Makes Inventrack Different?

Traditional inventory systems primarily focus on recording current inventory.

Inventrack adds a machine learning layer that uses historical demand data to help answer:

```text
How much demand should we expect?

Which forecasting model performs best?

When could the current stock run out?

How much inventory should we consider reordering?
```

This turns the system from a basic inventory CRUD application into an **inventory management and predictive demand-planning platform**.

---

## Project Highlights

* Full-stack Flask application
* Modular backend architecture using Flask Blueprints
* SQLAlchemy-based database layer
* User authentication
* Product and SKU management
* Stock movement tracking
* Purchase order workflow
* CSV/XLSX data ingestion
* Data validation and preprocessing
* Machine learning demand forecasting
* Linear Regression, Random Forest and XGBoost
* Automatic model selection
* MAE, RMSE and MAPE evaluation
* Stockout prediction
* Reorder quantity recommendation
* Inventory notifications

---

## Author

**Nitesh Bhoir**

B.Tech Computer Science Engineering — Data Science

Amity University Mumbai

---

## License

This project is developed for educational, portfolio, and demonstration purposes.
