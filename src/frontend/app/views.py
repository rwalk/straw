#!/usr/bin/python
'''
Define the views for the straw web app
'''
from flask import render_template, session, request, render_template, jsonify, Flask, make_response
from time import sleep
from kafka.common import FailedPayloadsError, NotLeaderForPartitionError, KafkaUnavailableError
import md5, redis
import json, uuid

MAX_RESULTS = 100

def attach_views(app):

    @app.route('/_fetch_messages')
    def fetch_messages():
        # get a redis connection
        redis_connection = redis.Redis(connection_pool=app.pool)

        # update the query list in the view
        if session.get('sid') is not None:
            matches = redis_connection.lrange(session.get('sid'), 0, MAX_RESULTS)
        return jsonify(result=matches)

    @app.route('/', methods=['GET'])
    def index():
        print(session)
        if session.get('sid') is None:
            session['sid'] = uuid.uuid4().hex
        try:
            query_list = session['queries']
        except KeyError:
            query_list = []
        return render_template('index.html', query_list=query_list)

    @app.route('/', methods=['POST'])
    def search_box_control():
        '''add to or clear the list of queries.'''

        # we need a session
        if session.get('sid') is None:
            raise RuntimeError("No session.")
        sid = session.get('sid')       


        # get a redis connection
        redis_connection = redis.Redis(connection_pool=app.pool)
         
        # if clear button pressed:
        if 'clear' in request.form:
            app.clear_user(session.get('sid'))
            if session.has_key('queries'):
                del session['queries']
            return render_template("index.html", query_list=[])

        # create a new query
        text = request.form['text'].lower().split(" ")

        # generate a unique query id
        msg = {"type":"terms-query","terms":text,"minimum-match":len(text)}
        data = json.dumps(msg)
        qid = md5.new(data).hexdigest()
        query_string = " ".join(text)

        # add the qid and value to the query lookup store
        try:
            session['queries'].append(query_string)
        except KeyError:
            session['queries'] = [query_string]

        # try three times to do the post to kafka.
        post_success = False
        for i in range(3):
            try:
                app.producer.send_messages("queries", data)
            except (FailedPayloadsError, NotLeaderForPartitionError, KafkaUnavailableError) as e:
                # wait a bit and try again
                print("Failed to post query {0} to kafka. Try #{1}".format(data, i))
                sleep(0.25)
                continue
            post_success=True
            break

        if post_success==True:
            # subscribe the user to the query            
            try:
                app.user_channels[qid].add(sid)
            except KeyError:
                app.user_channels[qid] = set([sid])
                app.subscriber.add_query(qid)

            # link the id to the query text
            redis_connection.set(qid, " ".join(text))

            # add query to the list of things the user has subscribed to
            redis_connection.lpush(sid +"-queries", qid)

        # update the query list in the view
        query_list = session["queries"]
        return render_template("index.html", query_list=query_list)

    @app.route('/about')
    def about():
        return render_template('%s.html' % 'about')
