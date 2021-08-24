from typing import Dict, List
from flask import Flask, jsonify, request
from .loader import Loader
import os
from flask_caching import Cache


CACHE_DEFAULT_TIMEOUT = (60*3)+13
config = {
    "DEBUG": True,
    "CACHE_TYPE": "FileSystemCache",
    "CACHE_DEFAULT_TIMEOUT": CACHE_DEFAULT_TIMEOUT,
    "CACHE_DIR": os.path.dirname(os.path.realpath(__file__)) + '/../cache'
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

@app.route('/')
def main():
    return jsonify({
        'doc': 'Yahoo Finance API Documentation',
        'endpoints': [
            {
                '/': 'This document.',
                '/api/stocks?region=Brazil': 'List of symbol, name and prices',
            }
        ]
    })


@app.route('/stocks')
@cache.memoize(CACHE_DEFAULT_TIMEOUT)
def stocks():
    try:
        region: str = request.args["region"]
        loader: Loader = Loader()
        results: Dict = loader.load_stocks_from_region(region)

        return jsonify(results)
    except KeyError as e:
        return jsonify("Region param is required"), 400
    except ValueError as e:
        return jsonify(str(e)), 400




