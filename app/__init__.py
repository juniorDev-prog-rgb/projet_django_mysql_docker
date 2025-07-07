from flask import Flask
from flask_socketio import SocketIO
from app.models.device import db
from app.tasks.scheduler import MonitoringScheduler
import logging

socketio = SocketIO()
scheduler = MonitoringScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Configuration des logs
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s'
    )

    # Initialisation de la base de données
    db.init_app(app)

    # Enregistrement des blueprints
    from app.routes.devices import device_bp
    app.register_blueprint(device_bp)

    # Initialisation de SocketIO
    socketio.init_app(app, cors_allowed_origins="*")

    # Importation des handlers SocketIO
    from app.sockets import live_status

    # Initialisation du planificateur
    scheduler.init_app(app)

    # Création des tables de base de données
    with app.app_context():
        db.create_all()

    return app
