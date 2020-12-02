from flask import Flask, escape, request
from flask_redis import FlaskRedis

redis_client = FlaskRedis()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")

    with app.app_context():
        redis_client.init_app(app)

        from application.spreadsheet.backend import BackendServer

        backendServer = BackendServer()
        backendServer.start()

        from application.spreadsheet.client import SyncService

        syncService = SyncService()
        syncService.start()

        import application.spreadsheet.routes as spreadsheet_routes

        app.register_blueprint(spreadsheet_routes.spreadsheet_bp)

        import application.ldap.routes as ldap_routes

        app.register_blueprint(ldap_routes.ldap_bp)

        return app
