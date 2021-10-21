from flask import Flask
from flask_redis import FlaskRedis

redis_client = FlaskRedis()


def create_app():

    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.ProductionConfig")

    with app.app_context():
        redis_client.init_app(app)

        if app.config.get("ENABLE_SPREADSHEET", False):
            _app_register_spreadsheet(app)

        if app.config.get("ENABLE_LDAP", False):
            _app_register_ldap(app)

        if app.config.get("ENABLE_JWT_TOKEN", False):
            _app_register_jwt_token(app)

        return app


def _app_register_jwt_token(app):
    pass


def _app_register_spreadsheet(app):
    from application.spreadsheet.backend import BackendServer

    backendServer = BackendServer()
    backendServer.start()

    from application.spreadsheet.client import SyncService

    syncService = SyncService()
    syncService.start()

    import application.spreadsheet.routes as spreadsheet_routes

    app.register_blueprint(spreadsheet_routes.spreadsheet_bp)


def _app_register_ldap(app):
    import application.ldap_bp.routes as ldap_routes

    app.register_blueprint(ldap_routes.ldap_bp)
