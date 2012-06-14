# All of our imports

import bottle

# 'route' is for the anotation (@route), request there so we can get the json, run is there so we can run this thing
from bottle import route, run,  request

# This lets us connect to the db
import pymongo
from pymongo import Connection

# this says that the path to make a HTTP POST request to is /trapreport
@route('/trapreport',  method='POST')
def trapreport():
    
    # ---------------------------------- All of this should go into a celery worker function --------------------------------------------------- #
    
    # as long as the person (application) making the post request has the header: "Content-Type: application/json", we can get the json info directly from the request.
    # This trap variable is a pythin dict object. We can access stuff like this: trap['bearing']. We should definitly do some data validation here.
    trap = request.json
    
    # get a connection to mongod which must be running
    connection = Connection()
    
    # get a handle on our database
    db = connection.radar
    
    # get a handle on our collection
    collection = db.rawTrapData
    
    # insert our new data
    collection.insert(trap)
    
    # -------------------------------------------End what should go in a celery worker function-------------------------------------------------------------- #
    
    # return something?
    return str("OK")

# run the server.
run()

# now to test this out:

# run mongod
# make a file called trap.txt
# run this script
# run curl -H "Content-Type: application/json" -X POST -d @trap.txt http://127.0.0.1:8080/trapreport


# sources

# bottle tutorial: http://bottlepy.org/docs/dev/tutorial_app.html

# info on bottle/json: http://bottlepy.org/docs/0.10/api.html?highlight=json#bottle.BaseRequest.json

# pymongo tutorial: http://api.mongodb.org/python/current/tutorial.html
