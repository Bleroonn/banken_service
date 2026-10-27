from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "banken-service läuft"

    return app


if __name__ == "__main__":
    create_app().run(debug=False)
