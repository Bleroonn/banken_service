import logging
import os
from logging.handlers import RotatingFileHandler
 
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError, CSRFProtect
 
from routes import bp
 
load_dotenv()
 
csrf = CSRFProtect()
 
 
def setup_logging():
    os.makedirs("logs", exist_ok=True)
    handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=5, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger = logging.getLogger("bank")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
 
 
def create_app():
    setup_logging()
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    csrf.init_app(app)
    app.register_blueprint(bp)
 
    @app.errorhandler(404)
    def not_found(error):
        return render_template("fehler.html", message="Die Seite wurde nicht gefunden."), 404
 
    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return render_template("fehler.html", message="Die Anfrage ist ungültig oder abgelaufen. Bitte laden Sie die Seite neu."), 400
 
    @app.errorhandler(500)
    def server_error(error):
        logging.getLogger("bank").error("Technischer Fehler: %s", error.original_exception)
        return render_template("fehler.html", message="Es ist ein technischer Fehler aufgetreten. Bitte versuchen Sie es später erneut."), 500
 
    return app
 
 
if __name__ == "__main__":
    create_app().run()