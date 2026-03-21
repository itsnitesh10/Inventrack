from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category, Stock

products = Blueprint('products', __name__, url_prefix='/products')


@products.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', '')
    query = Product.query.filter_by(is_active=True)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.sku.ilike(f'%{search}%'))
    if category_id:
        query = query.filter_by(category_id=category_id)
    all_products = query.order_by(Product.name).all()
    categories = Category.query.all()
    return render_template('products/index.html', products=all_products,
                           categories=categories, search=search, category_id=category_id)


@products.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        sku = request.form.get('sku')
        description = request.form.get('description')
        unit_price = float(request.form.get('unit_price', 0))
        reorder_level = int(request.form.get('reorder_level', 10))
        category_id = request.form.get('category_id') or None
        initial_stock = int(request.form.get('initial_stock', 0))

        if Product.query.filter_by(sku=sku).first():
            flash('SKU already exists.', 'danger')
            return render_template('products/form.html', categories=categories, action='Add')

        product = Product(name=name, sku=sku, description=description,
                          unit_price=unit_price, reorder_level=reorder_level,
                          category_id=category_id)
        db.session.add(product)
        db.session.flush()

        stock = Stock(product_id=product.id, quantity=initial_stock)
        db.session.add(stock)
        db.session.commit()

        flash(f'Product "{name}" added successfully!', 'success')
        return redirect(url_for('products.index'))
    return render_template('products/form.html', categories=categories, action='Add')


@products.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.all()
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.sku = request.form.get('sku')
        product.description = request.form.get('description')
        product.unit_price = float(request.form.get('unit_price', 0))
        product.reorder_level = int(request.form.get('reorder_level', 10))
        product.category_id = request.form.get('category_id') or None
        db.session.commit()
        flash(f'Product "{product.name}" updated!', 'success')
        return redirect(url_for('products.index'))
    return render_template('products/form.html', product=product,
                           categories=categories, action='Edit')


@products.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    product = Product.query.get_or_404(id)
    product.is_active = False
    db.session.commit()
    flash(f'Product "{product.name}" removed.', 'info')
    return redirect(url_for('products.index'))


@products.route('/view/<int:id>')
@login_required
def view(id):
    product = Product.query.get_or_404(id)
    return render_template('products/view.html', product=product)


# --- Categories ---
@products.route('/categories')
@login_required
def categories():
    all_cats = Category.query.all()
    return render_template('products/categories.html', categories=all_cats)


@products.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if Category.query.filter_by(name=name).first():
            flash('Category already exists.', 'danger')
        else:
            cat = Category(name=name, description=description)
            db.session.add(cat)
            db.session.commit()
            flash(f'Category "{name}" added!', 'success')
        return redirect(url_for('products.categories'))
    return render_template('products/category_form.html')


@products.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    cat = Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    flash(f'Category "{cat.name}" deleted.', 'info')
    return redirect(url_for('products.categories'))