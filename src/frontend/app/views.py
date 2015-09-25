#!/usr/bin/python

from flask import render_template, request, render_template, jsonify
from time import sleep
from app import app
import json


@app.route('/_fetch_messages')
def fetch_messages():
    return jsonify(result=app.disp)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def my_form_post():

    text = request.form['text']
    processed_text = text.upper()
    return processed_text

