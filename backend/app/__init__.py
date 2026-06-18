from flask import Flask
from app.config import Config
from app.extensions import db, migrate, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, supports_credentials=True)

    from app.api.auth import auth_bp
    from app.api.department import dept_bp
    from app.api.person_category import category_bp
    from app.api.key_person import person_bp
    from app.api.person_contact import contact_bp
    from app.api.person_case import case_bp
    from app.api.person_track import track_bp
    from app.api.person_alert import alert_bp
    from app.api.user import user_bp
    from app.api.tag import tag_bp
    from app.api.attachment import attach_bp
    from app.api.import_export import import_bp
    from app.api.operation_log import log_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dept_bp, url_prefix='/api/departments')
    app.register_blueprint(category_bp, url_prefix='/api/categories')
    app.register_blueprint(person_bp, url_prefix='/api/persons')
    app.register_blueprint(contact_bp, url_prefix='/api/contacts')
    app.register_blueprint(case_bp, url_prefix='/api/cases')
    app.register_blueprint(track_bp, url_prefix='/api/tracks')
    app.register_blueprint(alert_bp, url_prefix='/api/alerts')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(tag_bp, url_prefix='/api/tags')
    app.register_blueprint(attach_bp, url_prefix='/api/attachments')
    app.register_blueprint(import_bp, url_prefix='/api/import-export')
    app.register_blueprint(log_bp, url_prefix='/api/logs')

    from app.api.visit_task import visit_bp
    from app.api.visit_record import record_bp
    from app.api.risk_assessment import risk_bp
    from app.api.notification import notif_bp
    from app.api.lost_contact import lost_bp
    from app.api.alert_review import review_bp
    from app.api.cross_region import cross_region_bp
    from app.api.device import device_bp

    app.register_blueprint(visit_bp, url_prefix='/api/visit-tasks')
    app.register_blueprint(record_bp, url_prefix='/api/visit-records')
    app.register_blueprint(risk_bp, url_prefix='/api/risk-assessment')
    app.register_blueprint(notif_bp, url_prefix='/api/notifications')
    app.register_blueprint(lost_bp, url_prefix='/api/lost-contacts')
    app.register_blueprint(review_bp, url_prefix='/api/alerts/review')
    app.register_blueprint(cross_region_bp, url_prefix='/api/cross-region')
    app.register_blueprint(device_bp, url_prefix='/api/devices')

    return app
