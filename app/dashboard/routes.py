from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime, timedelta
from app import db
from app.models import Product, Stock, Order, StockMovement, Category

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@dashboard.route('/dashboard')
@login_required
def index():
    total_products = Product.query.filter_by(is_active=True).count()
    all_stock = db.session.query(Stock).join(Product).filter(Product.is_active == True).all()
    low_stock_count = sum(1 for s in all_stock if s.is_low)
    out_of_stock_count = sum(1 for s in all_stock if s.quantity == 0)
    total_inventory_value = sum((s.quantity * s.product.unit_price) for s in all_stock) or 0
    pending_orders = Order.query.filter_by(status='pending').count()
    total_orders = Order.query.count()
    received_orders = Order.query.filter_by(status='received').count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    low_stock_products = [s for s in all_stock if s.is_low][:6]
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_movements = (StockMovement.query
        .filter(StockMovement.created_at >= week_ago)
        .order_by(StockMovement.created_at.desc()).limit(8).all())
    return render_template('dashboard/index.html',
        total_products=total_products,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        total_inventory_value=total_inventory_value,
        pending_orders=pending_orders,
        total_orders=total_orders,
        received_orders=received_orders,
        recent_orders=recent_orders,
        low_stock_products=low_stock_products,
        recent_movements=recent_movements,
    )

@dashboard.route('/dashboard/api/stock-by-category')
@login_required
def api_stock_by_category():
    results = (db.session.query(Category.name, func.sum(Stock.quantity))
        .join(Product, Product.category_id == Category.id)
        .join(Stock, Stock.product_id == Product.id)
        .filter(Product.is_active == True)
        .group_by(Category.name).all())
    return jsonify({'labels': [r[0] for r in results], 'values': [int(r[1]) for r in results]})

@dashboard.route('/dashboard/api/movements-trend')
@login_required
def api_movements_trend():
    days = 30
    start = datetime.utcnow() - timedelta(days=days)
    results = (db.session.query(
            func.date(StockMovement.created_at).label('day'),
            StockMovement.movement_type,
            func.sum(StockMovement.quantity).label('total'))
        .filter(StockMovement.created_at >= start)
        .group_by(func.date(StockMovement.created_at), StockMovement.movement_type)
        .order_by('day').all())
    date_range = [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days+1)]
    ins  = {str(r.day): int(r.total) for r in results if r.movement_type == 'in'}
    outs = {str(r.day): int(r.total) for r in results if r.movement_type == 'out'}
    return jsonify({'labels': date_range,
        'in':  [ins.get(d, 0)  for d in date_range],
        'out': [outs.get(d, 0) for d in date_range]})

@dashboard.route('/dashboard/api/top-products')
@login_required
def api_top_products():
    results = (db.session.query(Product.name, func.sum(StockMovement.quantity).label('total'))
        .join(StockMovement, StockMovement.product_id == Product.id)
        .filter(StockMovement.movement_type == 'out')
        .group_by(Product.name)
        .order_by(func.sum(StockMovement.quantity).desc()).limit(8).all())
    return jsonify({'labels': [r[0] for r in results], 'values': [int(r[1]) for r in results]})

@dashboard.route('/dashboard/api/order-status')
@login_required
def api_order_status():
    statuses = ['pending', 'received', 'cancelled']
    counts = [Order.query.filter_by(status=s).count() for s in statuses]
    return jsonify({'labels': ['Pending','Received','Cancelled'], 'values': counts})
