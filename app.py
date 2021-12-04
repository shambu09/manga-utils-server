import logging

import requests
from flask import Flask, make_response, request

get_public_url_file = lambda file_id: f"https://drive.google.com/uc?export=view&id={file_id}"


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return """<h1>Manga Crawler Server</h1><a href="https://github.com/shambu09/manga-crawler">Repo</a>"""

    @app.route('/get_metadata', methods=['GET'])
    def get_file():
        file_id = request.args.get('file_id', "")
        resp = {}

        if file_id == '': return resp

        try:
            resp = requests.get(get_public_url_file(file_id)).json()

        except:
            resp = make_response("Error: File not found", 404)

        else:
            resp = make_response(
                resp,
                200,
            )

            headers = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': '*',
                'Access-Control-Allow-Headers': '*',
            }

            resp.headers = headers

        return resp

    @app.errorhandler(404)
    def Error(error):
        return "<h1>404 Error: Page Not ound</h1>"

    return app
