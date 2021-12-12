import logging
import os
from functools import wraps
import re

from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request
from flask_pymongo import PyMongo


def init_logger(app):
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)


def cross_orgin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response

        resp = func(*args, **kwargs)
        resp.headers.add("Access-Control-Allow-Origin", "*")
        return resp

    return wrapper


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
    mongo = PyMongo(app)
    db = mongo.db
    init_logger(app)

    @app.route('/', methods=['GET', 'OPTIONS'])
    @cross_orgin
    def index():
        return make_response(
            """<h1>Manga Crawler Server</h1><a href="https://github.com/shambu09/manga-crawler">Repo</a>""",
            200)

    @app.route("/get_index", methods=["GET", "OPTIONS"])
    @cross_orgin
    def get_index():
        index = db["content"].find_one({"_meta": 0}, {
            "_meta": 0,
            "_id": 0,
        })
        return make_response(jsonify(index), 200)

    @app.route("/change_index", methods=["PUT", "PATCH", "OPTIONS"])
    @cross_orgin
    def change_index():
        data = request.get_json()
        if not data:
            return make_response(jsonify({"message": "No data found"}), 400)

        if request.method == "PUT":
            if data.get("_id", "no_id") == "no_id":
                return make_response(jsonify({"message": "No id found"}), 400)

            if data.get("_meta", "no_meta") == "no_meta":
                data.update({"_meta": 0})

            db["content"].replace_one({"_meta": 0}, data)
            app.logger.info("Index Regenerated")
            return make_response(jsonify({"message": "Index Regenerated"}),
                                 200)

        if request.method == "PATCH":
            db["content"].update_one({"_meta": 0}, {"$set": data})
            app.logger.info("Index Altered")
            return make_response(jsonify({"message": "Index Altered"}), 200)

    @app.route('/get_metadata', methods=['GET', "OPTIONS"])
    @cross_orgin
    def get_file():
        file_id = request.args.get('file_id', "")
        resp = {}

        if file_id == '':
            resp = make_response(jsonify({"message": "No file found"}), 400)

        try:
            resp = db["content"].find_one({"_id": file_id}, {
                "_meta": 0,
                "_id": 0,
            })
            resp = jsonify(resp)

        except Exception as e:
            app.logger.error(f"Error: {e}")
            resp = make_response(jsonify({"message": "No file found"}), 400)

        else:
            resp = make_response(
                resp,
                200,
            )

        return resp

    @app.route("/add_manga", methods=["PUT", "OPTIONS"])
    @cross_orgin
    def put_file():
        data = request.get_json()
        if not data:
            return make_response(jsonify({"message": "No data found"}), 400)

        if data.get("_id", "no_id") == "no_id":
            return make_response(jsonify({"message": "No _id found"}), 400)

        if data.get("_meta", "no_meta") == "no_meta":
            data.update({"_meta": 1})

        db["content"].insert_one(data)
        app.logger.info("Manga Added")
        return make_response(jsonify({"message": "success"}), 200)

    @app.errorhandler(404)
    def Error(error):
        return make_response("<h1>404 Error: Page Not Found</h1>", 404)

    return app
