from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'inventrack-secret-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.auth.routes import auth
    from app.products.routes import products
    from app.stock.routes import stock
    from app.orders.routes import orders
    from app.forecasting.routes import forecasting
    from app.dashboard.routes import dashboard

    app.register_blueprint(auth)
    app.register_blueprint(products)
    app.register_blueprint(stock)
    app.register_blueprint(orders)
    app.register_blueprint(forecasting)
    app.register_blueprint(dashboard)

    with app.app_context():
        db.create_all()

    return app
