#!/usr/bin/python
'''
Define the views for the straw web app
'''
from flask import render_template, request, render_template, jsonify, Flask
from time import sleep
import md5, redis
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

        # get a redis connection
        redis_connection = redis.Redis(connection_pool=app.pool)

        # userid state
        userid = request.args.get('userid')

        if userid is None:
            userid = md5.new("demo-mode-no-user").hexdigest()

        # create a new query
        text = request.form['text'].split(" ")
        msg = {"type":"terms-query","terms":text,"minimum-match":len(text)}
        data = json.dumps(msg)
        qid = md5.new(data).hexdigest()
        
        # add the qid and value to the query lookup store
        redis_connection.set(qid, text)

        # add the query text to the users query store
        redis_connection.lpush(userid, request.form['text'])

        # register the query with the Straw platform
        app.producer.send_messages("queries", data)

        # subscribe the user to the query
        app.subscriber.add_query(qid)

        # update the query list in the view
        query_list = redis_connection.lrange(userid, 0, -1)
        print(query_list)
        return render_template("index.html", query_list=query_list)

