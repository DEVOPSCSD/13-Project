"""Flask application factory and entry point."""
from flask import Flask, jsonify, request
from flask_cors import CORS

import database
from config import Config
from routes import api


def create_app(test_config=None):
    frontend_dir = (test_config or {}).get("FRONTEND_DIR", Config.FRONTEND_DIR)
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    database.init_app(app)
    app.register_blueprint(api)

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    def api_error(code, message, status):
        return jsonify({"success": False,
                        "error": {"code": code, "message": message, "details": {}}}), status

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return api_error("NOT_FOUND", "Resource not found.", 404)
        return "Not found", 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return api_error("METHOD_NOT_ALLOWED", "Method not allowed for this endpoint.", 405)

    @app.errorhandler(500)
    def server_error(e):
        return api_error("SERVER_ERROR", "Unexpected server error.", 500)

    return app


if __name__ == "__main__":
    create_app().run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
