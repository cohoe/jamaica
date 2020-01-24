from flask import render_template
from jamaica import app

@app.route('/')
def index():
    return "Hello"
