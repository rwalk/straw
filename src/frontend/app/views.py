#!/usr/bin/python

from flask import render_template, request, render_template, jsonify, Flask
from time import sleep
import md5
import json

def attach_views(app):

    @app.route('/_fetch_messages')
    def fetch_messages():
        return jsonify(result=app.disp[::-1])

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/', methods=['POST'])
    def my_form_post():

        # userid state
        userid = request.args.get('userid')
        
        # create a new query
        text = request.form['text'].split(" ")
        msg = {"type":"terms-query","terms":text,"minimum-match":len(text)}
        data = json.dumps(msg)
        qid = md5.new(data).hexdigest()

        # register the query
        app.producer.send_messages("queries", data)
        app.subscriber.add_query(qid)
        return render_template("index.html")

