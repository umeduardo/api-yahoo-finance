import pytest
from typing import Dict, List
from flask import Flask, jsonify, request
from ..loader import Loader
import os
import time


def test_open_browser():
    loader: Loader = Loader()
    loader.browser.get(loader.finance_url)
    loader.browser.maximize_window()
    assert loader.browser.title == 'Free Stock Screener - Yahoo Finance'
    loader.browser.quit()


def test_load_stocks():
    loader: Loader = Loader()
    data: Dict = loader.load_stocks_from_region('Malaysia')
    for index, row in data.items():
        assert index == row['symbol']
    
def test_load_regions():
    loader: Loader = Loader()
    data: List = loader.load_all_regions()
    assert len(data) > 0