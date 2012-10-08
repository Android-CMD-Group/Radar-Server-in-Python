import json
import server
import unittest

# This lets us connect to the db
import pymongo
from pymongo import Connection

# get a connection to mongod which must be running
connection = Connection()

# get a handle on our database
db = connection.radar

class Test(unittest.TestCase):
    def setUp(self):
        collection = db.testTraps
        collection.insert(json.load(open('test/test_traps.json'))['traps'])
        collection.ensure_index( [( "loc" , "2d" )] )

    def _tearDown(self):
        collection = db.testTraps
        collection.remove()


    def test_gettraps(self):

        collection = db.testTraps

        server.gettraps({"loc": [33.5905, -117.2404], "speed": 20, "bearing": 304.58087947835827, "id": "1asasd23"}, collection=collection)

if __name__ == '__main__':
    unittest.main()
