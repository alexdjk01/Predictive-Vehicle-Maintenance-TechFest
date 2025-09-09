from flask import Flask
from flask_cors import CORS

from pvmt.app.routes import app_routes

def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)  # enable CORS for all routes
    app.register_blueprint(app_routes)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)