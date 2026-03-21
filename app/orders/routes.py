from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Order, OrderItem, Product, Stock, StockMovement

orders = Blueprint('orders', __name__, url_prefix='/orders')


def generate_order_number():
    last = Order.query.order_by(Order.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f'PO-{datetime.utcnow().year}-{num:04d}'


@orders.route('/')
@login_required
def index():
    status = request.args.get('status', '')
    query = Order.query
    if status:
        query = query.filter_by(status=status)
    all_orders = query.order_by(Order.created_at.desc()).all()
    return render_template('orders/index.html', orders=all_orders, status=status)


@orders.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    products = Product.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        supplier = request.form.get('supplier')
        notes = request.form.get('notes', '')
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        unit_prices = request.form.getlist('unit_price[]')

        if not product_ids or not any(q.strip() for q in quantities):
            flash('Please add at least one product to the order.', 'danger')
            return render_template('orders/form.html', products=products)

        order = Order(
            order_number=generate_order_number(),
            supplier=supplier,
            notes=notes,
            created_by=current_user.id,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()

        for pid, qty, price in zip(product_ids, quantities, unit_prices):
            if pid and qty and int(qty) > 0:
                item = OrderItem(
                    order_id=order.id,
                    product_id=int(pid),
                    quantity=int(qty),
                    unit_price=float(price) if price else 0.0
                )
                db.session.add(item)

        db.session.commit()
        flash(f'Order {order.order_number} created!', 'success')
        return redirect(url_for('orders.view', id=order.id))

    return render_template('orders/form.html', products=products)


@orders.route('/view/<int:id>')
@login_required
def view(id):
    order = Order.query.get_or_404(id)
    return render_template('orders/view.html', order=order)


@orders.route('/receive/<int:id>', methods=['POST'])
@login_required
def receive(id):
    order = Order.query.get_or_404(id)
    if order.status != 'pending':
        flash('Only pending orders can be received.', 'warning')
        return redirect(url_for('orders.view', id=id))

    for item in order.items:
        stock_entry = Stock.query.filter_by(product_id=item.product_id).first()
        if not stock_entry:
            stock_entry = Stock(product_id=item.product_id, quantity=0)
            db.session.add(stock_entry)
        stock_entry.quantity += item.quantity
        stock_entry.last_updated = datetime.utcnow()

        movement = StockMovement(
            product_id=item.product_id,
            movement_type='in',
            quantity=item.quantity,
            reference=order.order_number,
            created_by=current_user.id,
            notes=f'Received from order {order.order_number}'
        )
        db.session.add(movement)

    order.status = 'received'
    order.received_at = datetime.utcnow()
    db.session.commit()
    flash(f'Order {order.order_number} marked as received. Stock updated!', 'success')
    return redirect(url_for('orders.view', id=id))


@orders.route('/cancel/<int:id>', methods=['POST'])
@login_required
def cancel(id):
    order = Order.query.get_or_404(id)
    if order.status != 'pending':
        flash('Only pending orders can be cancelled.', 'warning')
    else:
        order.status = 'cancelled'
        db.session.commit()
        flash(f'Order {order.order_number} cancelled.', 'info')
    return redirect(url_for('orders.view', id=id))


@orders.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted.', 'info')
    return redirect(url_for('orders.index'))