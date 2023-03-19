#!/usr/bin/env flask
'''
A flask app to serve dziv
'''
from flask import Flask, request
# from flask_restful import Resource, Api

app = Flask(__name__)

source = None

def linkify(filename):
    return f'<a href="{filename}">{filename}</a>'

@app.route("/")
def top():
    src = source
    if isinstance(src, str):
        src = [src]
    lines = ['<p>' + linkify(one) + '</p>' for one in src]

    return '\n'.join(lines)

@app.route("/<name>.dzi")
def dzi_file(name):
    return f"<p>This would show dzi file {name}.dzi</p>"
