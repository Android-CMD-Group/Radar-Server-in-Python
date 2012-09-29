# All of our imports
import time
import math
import bottle

# 'route' is for the anotation (@route), request there so we can get the json, run is there so we can run this thing
from bottle import route, run, request

# This lets us connect to the db
import pymongo
from pymongo import Connection

# this says that the path to make a HTTP POST request to is /trapreport
@route('/trapreport', method='POST')
def trapreport():
    # ---------------------------------- All of this should go into a celery worker function --------------------------------------------------- #

    # as long as the person (application) making the post request has the header: "Content-Type: application/json", we can get the json info directly from the request.
    # This trap variable is a python dict object. We can access stuff like this: trap['bearing']. We should definitly do some data validation here.
    trap = request.json

    # get a connection to mongod which must be running
    connection = Connection()

    # get a handle on our database
    db = connection.radar

    # get a handle on our collection
    collection = db.rawTrapData

    # insert our new data
    collection.insert(trap)

    # Log the client/user's location into the :last known location" database so we can notify them in real time if
    # they are heading towards a trap that is reported in the near future near them

    # Maybe the two next things should be in a celery function?

    # Now we should process the new data and adjust the weights and locations of the aggregated trap database.

    # Then notify all users that might be affected, Figure this out by using the info in "last known location database"

    # -------------------------------------------End what should go in a celery worker function-------------------------------------------------------------- #

    # return something?
    return str("OK")

# Haversine formula example in Python, gives distance in km
# Author: Wayne Dyck
# Works awesomely
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371 # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1))\
                                                  * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(
        dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d



def bearingBetweenTwoPoints(end, start):
    distanceFromOldPointToRightTrianglePoint = distance([start[0], start[1]], [start[0], end[1]])
    distanceFromOldPointToCurrentPoint = distance([start[0], start[1]], [end[0], end[1]])

    rawAngle = math.acos(distanceFromOldPointToRightTrianglePoint / distanceFromOldPointToCurrentPoint)
    rawAngle = math.degrees(rawAngle)

    quadrant = 0

    if start[0] < end[0]:
        if start[1] < end[1]:
            quadrant = 1
        else:
            quadrant = 2
    else:
        if start[1] > end[1]:
            quadrant = 3
        else:
            quadrant = 4

    bearing = 361

    if quadrant == 1:
        bearing = rawAngle
    elif quadrant == 2:
        bearing = 180 - rawAngle
    elif quadrant == 3:
        bearing = 180 + rawAngle
    elif quadrant == 4:
        bearing = 360 - rawAngle

    return bearing

# The max number of traps to give to the client
TRAP_LIMIT = 100

SECONDS_IN_HOUR = 3600

# tolerance level for how similar the direction the new client must be
# going in comparison to the client that reported the trap
VALID_REPORTED_BEARING_RANGE = 120

# the search range in which to consider points to send clients (in degrees)
VALID_LOCATION_BEARING_RANGE = 120

@route('/gettraps', method='POST')
def gettraps():
    # need to be validated
    clientInfo = request.json

    clientLocation = clientInfo['loc']
    clientSpeed = clientInfo['speed']
    clientBearing = clientInfo['bearing']

    # get a connection to mongod which must be running
    connection = Connection()

    # get a handle on our database
    db = connection.radar


    # get a handle on our collection
    collection = db.rawTrapData

    # get all the traps that are within an hour (at current speed of
    # client)
    nearestTraps = collection.find({"loc": {"$near": clientLocation, "$maxDistance": clientSpeed * SECONDS_IN_HOUR}})

    # filter out all traps for which the new client is traveling in a
    # different direction than the cleint that reported the trap
    filteredTraps = []

    upperBearingBound = (clientBearing + (.5 * VALID_REPORTED_BEARING_RANGE)) % 360
    lowerBearingBound = (clientBearing - (.5 * VALID_REPORTED_BEARING_RANGE)) % 360

    for trap in nearestTraps:
        if trap['bearing'] > lowerBearingBound and trap['bearing'] < upperBearingBound:
            filteredTraps.append(trap)

    # filter out all the traps that are not with some degrees of the client's heading

    upperBearingBound = (clientBearing + (.5 * VALID_LOCATION_BEARING_RANGE)) % 360
    lowerBearingBound = (clientBearing - (.5 * VALID_LOCATION_BEARING_RANGE)) % 360

    for trap in filteredTraps:
        bearingBetweenTraps = bearingBetweenTwoPoints(clientLocation, trap['loc'])
        if bearingBetweenTraps > lowerBearingBound and bearingBetweenTraps < upperBearingBound:
            filteredTraps.remove(trap)

    # log the clients location into "last known location collection" so later
    # we can push to them if there is a new point found

    collection = db.lastlocation
    collection.insert({ clientInfo['id']: clientInfo })


    # return all the results to the client, auto converts to json (yey
    # bottle!)
    return { 'traps': filteredTraps }


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
