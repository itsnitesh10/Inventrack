from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.models import Product, StockMovement
from app.forecasting.model import forecast_product, get_forecast_summary
from app import db

forecasting = Blueprint('forecasting', __name__, url_prefix='/forecasting')


@forecasting.route('/')
@login_required
def index():
    products = Product.query.filter_by(is_active=True).all()
    products_with_data = []
    for p in products:
        count = StockMovement.query.filter_by(product_id=p.id, movement_type='out').count()
        if count >= 5:
            products_with_data.append(p)
    return render_template('forecasting/index.html',
                           products=products,
                           products_with_data=products_with_data)


@forecasting.route('/product/<int:product_id>')
@login_required
def product_forecast(product_id):
    product = Product.query.get_or_404(product_id)
    result = forecast_product(product_id)
    return render_template('forecasting/product.html', product=product, result=result)


@forecasting.route('/api/forecast/<int:product_id>')
@login_required
def api_forecast(product_id):
    result = forecast_product(product_id)
    return jsonify(result)


@forecasting.route('/summary')
@login_required
def summary():
    products = Product.query.filter_by(is_active=True).all()
    summaries = []
    for p in products:
        count = StockMovement.query.filter_by(product_id=p.id, movement_type='out').count()
        if count >= 5:
            s = get_forecast_summary(p.id)
            if s:
                summaries.append({'product': p, 'summary': s})
    return render_template('forecasting/summary.html', summaries=summaries)