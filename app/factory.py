import os
from quart import request, Response
from app.app import App
from app.routes.auth import auth_blueprint
from app.routes.catalog import catalog_bp
from app.routes.content_sync import content_sync_bp
from app.routes.manifest import manifest_blueprint
from app.routes.ui import ui_bp

def create_app() -> App:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, 'static')

    app_ = App(__name__, 
                template_folder="../templates", 
                static_folder=static_dir, 
                static_url_path='/static')
    
    app_.config.from_object("config.Config")
    
    @app_.errorhandler(405)
    async def handle_options_preflight(error):
        if request.method == "OPTIONS":
            resp = Response("", status=200)
            resp.headers["Access-Control-Allow-Origin"] = "*"
            resp.headers["Access-Control-Allow-Headers"] = "*"
            resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            return resp
        return "Method Not Allowed", 405

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
