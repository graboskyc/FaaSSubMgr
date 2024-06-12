import time
import datetime
import pymongo
import bson
from bson import json_util
from bson.json_util import loads
from bson import ObjectId
import os
import string
import random
import pickle
import sys
import base64

client = pymongo.MongoClient(sys.argv[1].strip())
handle = client['news-demo']['test']
runId = str(base64.b64encode(os.urandom(5)))

while True:
    newDoc = {}
    newDoc["tic"] = time.time()
    newDoc["created"] = datetime.datetime.now()
    newDoc["runId"] = runId
    
    # 1kb ascii block random worst case scenario for compression
    newDoc["noise"] =  bson.Binary(pickle.dumps(''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k = 1024*1))))
    
    # 16^7 = 268,435,456 possible _id values
    newDoc["_id"] = ''.join(random.choices("abcdefghkmnpqrst" , k = 7)) 

    output = handle.update_one({"_id":newDoc["_id"]}, {"$set": newDoc}, upsert=True)
    print(output.upserted_id)

    time.sleep(.5)