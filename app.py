import os

from dotenv import load_dotenv
from flask import Flask

from routes import bp

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    create_app().run()
