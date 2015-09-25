#!/usr/bin/python

from flask import render_template, request, render_template, jsonify
from time import sleep
from app import app
import md5
import json


@app.route('/_fetch_messages')
def fetch_messages():
    print(app.disp[::-1])
    return jsonify(result=app.disp[-10::-1])

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text'].split(" ")
    msg = {"type":"terms-query","terms":text,"minimum-match":len(text)}
    data = json.dumps(msg)
    qid = md5.new(data).hexdigest()
    app.producer.send_messages("queries", data)
    app.subscriber.add_query(qid)
    return render_template("index.html")

