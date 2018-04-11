####################################################################################################

import datetime
from pymongo import MongoClient

####################################################################################################

client = MongoClient('localhost', 27017)

db = client.test_database

post = {
    "author": "Mike",
    "text": "My first blog post!",
    "tags": ["mongodb", "python", "pymongo"],
    "date": datetime.datetime.utcnow(),
}

posts = db.posts
post_id = posts.insert_one(post).inserted_id

db.collection_names(include_system_collections=False)

posts.find_one()
posts.find_one({"author": "Mike"})
posts.find_one({"_id": post_id})
