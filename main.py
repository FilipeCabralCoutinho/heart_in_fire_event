import os

from flask import Flask

from db import db
from routes import routes
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.register_blueprint(routes)
app.secret_key = os.getenv("SECRET_KEY")
migrate = Migrate(app, db)

app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        db.create_all()

    app.run(debug=False)
