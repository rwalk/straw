#!/usr/bin/env python
from time import sleep
from app import app
from app.query_subscriber import QuerySubscriber
import thread

if __name__=="__main__":

    # Move messages to display box in background

    # other setup tasks
    app.disp = []
    app.subscriber = QuerySubscriber("localhost", 6379, app.disp)
    app.subscriber.add_query("f47366a4d493bb8a251cd1e2e543a1a5")
    app.run(host='0.0.0.0', debug = True)

