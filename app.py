import logging

import requests
from flask import Flask, make_response, request

get_public_url_file = lambda file_id: f"https://drive.google.com/uc?export=view&id={file_id}"


def init_logger(app):
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)

def create_app():
    app = Flask(__name__)
    init_logger(app)

    @app.route('/')
    def index():
        return """<h1>Manga Crawler Server</h1><a href="https://github.com/shambu09/manga-crawler">Repo</a>"""

    def _build_cors_preflight_response():
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

    def _corsify_actual_response(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    @app.route('/get_metadata', methods=['GET', "OPTIONS"])
    def get_file():
        if request.method == 'OPTIONS':
            return _build_cors_preflight_response()

        file_id = request.args.get('file_id', "")
        resp = {}

        if file_id == '':
            resp = make_response("Error: File not found", 404)
            return _corsify_actual_response(resp)

        try:
            resp = requests.get(get_public_url_file(file_id)).json()

        except Exception as e:
            app.logger.error(f"Error: {e}")
            resp = make_response("Error: File not found", 404)

        else:
            resp = make_response(
                resp,
                200,
            )

        resp = _corsify_actual_response(resp)
        return resp

    @app.errorhandler(404)
    def Error(error):
        return "<h1>404 Error: Page Not ound</h1>"

    return app
