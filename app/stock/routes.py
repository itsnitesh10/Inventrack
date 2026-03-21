from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Product, Stock, StockMovement

stock = Blueprint('stock', __name__, url_prefix='/stock')


@stock.route('/')
@login_required
def index():
    all_stock = db.session.query(Stock).join(Product).filter(Product.is_active == True).all()
    low_stock = [s for s in all_stock if s.is_low]
    return render_template('stock/index.html', all_stock=all_stock, low_stock=low_stock)


@stock.route('/adjust', methods=['GET', 'POST'])
@stock.route('/adjust/<int:product_id>', methods=['GET', 'POST'])
@login_required
def adjust(product_id=None):
    products = Product.query.filter_by(is_active=True).all()
    selected_product = Product.query.get(product_id) if product_id else None

    if request.method == 'POST':
        pid = int(request.form.get('product_id'))
        movement_type = request.form.get('movement_type')
        quantity = int(request.form.get('quantity'))
        notes = request.form.get('notes', '')
        reference = request.form.get('reference', '')

        product = Product.query.get_or_404(pid)
        stock_entry = Stock.query.filter_by(product_id=pid).first()

        if not stock_entry:
            stock_entry = Stock(product_id=pid, quantity=0)
            db.session.add(stock_entry)

        if movement_type == 'in':
            stock_entry.quantity += quantity
        elif movement_type == 'out':
            if stock_entry.quantity < quantity:
                flash('Not enough stock available!', 'danger')
                return redirect(url_for('stock.adjust', product_id=pid))
            stock_entry.quantity -= quantity
        elif movement_type == 'adjustment':
            stock_entry.quantity = quantity

        stock_entry.last_updated = datetime.utcnow()

        movement = StockMovement(
            product_id=pid,
            movement_type=movement_type,
            quantity=quantity,
            reference=reference,
            created_by=current_user.id,
            notes=notes
        )
        db.session.add(movement)
        db.session.commit()

        flash(f'Stock updated for "{product.name}"!', 'success')
        return redirect(url_for('stock.index'))

    return render_template('stock/adjust.html', products=products, selected_product=selected_product)


@stock.route('/movements')
@login_required
def movements():
    page = request.args.get('page', 1, type=int)
    product_id = request.args.get('product_id', '')
    movement_type = request.args.get('movement_type', '')

    query = StockMovement.query
    if product_id:
        query = query.filter_by(product_id=product_id)
    if movement_type:
        query = query.filter_by(movement_type=movement_type)

    movements = query.order_by(StockMovement.created_at.desc()).paginate(page=page, per_page=20)
    products = Product.query.filter_by(is_active=True).all()
    return render_template('stock/movements.html', movements=movements,
                           products=products, product_id=product_id,
                           movement_type=movement_type)


@stock.route('/alerts')
@login_required
def alerts():
    all_stock = db.session.query(Stock).join(Product).filter(Product.is_active == True).all()
    low_stock = [s for s in all_stock if s.is_low]
    out_of_stock = [s for s in all_stock if s.quantity == 0]
    return render_template('stock/alerts.html', low_stock=low_stock, out_of_stock=out_of_stock)


@stock.route('/api/levels')
@login_required
def api_levels():
    all_stock = db.session.query(Stock).join(Product).filter(Product.is_active == True).all()
    data = [{'product': s.product.name, 'quantity': s.quantity,
             'reorder_level': s.product.reorder_level, 'is_low': s.is_low} for s in all_stock]
    return jsonify(data)