from app.app import App
from app.routes.auth import auth_blueprint
from app.routes.catalog import catalog_bp
from app.routes.content_sync import content_sync_bp
from app.routes.manifest import manifest_blueprint
from app.routes.ui import ui_bp
from quart import request, Response 

def create_app() -> App:
    app_ = App(__name__, template_folder="../templates", static_folder="./static")
    app_.config.from_object("config.Config")
    
    @app_.before_request
    async def handle_preflight():
        if request.method == "OPTIONS":
            resp = Response("")
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Headers"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            return resp

    @app_.after_request
    async def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response
    
    app_.register_blueprint(auth_blueprint)
    app_.register_blueprint(manifest_blueprint)
    app_.register_blueprint(catalog_bp)
    app_.register_blueprint(content_sync_bp)
    app_.register_blueprint(ui_bp)

    return app_
