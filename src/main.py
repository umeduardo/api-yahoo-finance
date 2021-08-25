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
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    return jsonify({
        'doc': 'Yahoo Finance API Documentation',
        'endpoints': [
            {
                '/': 'This document.',
                '/api/stocks?region=Brazil': 'List of symbol, name and prices',
                '/api/regions': 'List all regions availables to consult',
            }
        ]
    })


@app.route('/stocks')
def stocks():
    cache_name: str = f"cache_{request.args.get('region','').lower()}"
    try:
        results = cache.get(cache_name)
        if results is None:
            region: str = request.args["region"]
            loader: Loader = Loader()
            results: Dict = loader.load_stocks_from_region(region)
            cache.set(cache_name, results, CACHE_DEFAULT_TIMEOUT)

        return jsonify(results)
    except KeyError as e:
        return jsonify("Region param is required"), 400
    except ValueError as e:
        cache.set(cache_name, str(e), CACHE_DEFAULT_TIMEOUT)
        return jsonify(str(e)), 400
    except RuntimeError as e:
        return jsonify(str(e)), 400


@app.route('/regions')
@cache.memoize(CACHE_DEFAULT_TIMEOUT)
def regions():
    loader: Loader = Loader()
    results: List = loader.load_all_regions()
    return jsonify(results)





