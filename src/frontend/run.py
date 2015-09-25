#!/usr/bin/env python
from time import sleep
from app import app
import thread

if __name__=="__main__":

    # Move messages to display box in background

    # other setup tasks
    
    app.disp = []

    # Define a function for the thread
    def load_msgs( threadName, app, msgs ):
        while len(msgs)>0:
            sleep(5)
            app.disp.append(msgs.pop())
        msgs = list("These are my messages")
        app.disp=[]

    msgs = list("These are my messages")
    thread.start_new_thread( load_msgs, ("Thread-1", app, msgs) )
    app.run(host='0.0.0.0', debug = True)

