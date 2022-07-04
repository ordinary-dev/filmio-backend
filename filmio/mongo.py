""" Module for connecting to a database and accessing collections """

import pymongo
from decouple import config

host = config('MONGODB_HOST', default='localhost')
port = config('MONGODB_PORT', default=27017, cast=int)
mongodb = pymongo.MongoClient(host, port)
db = mongodb.nullchan

# Collections
users = db.users
photos = db.photos
posts = db.posts
