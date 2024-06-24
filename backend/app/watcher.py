import pymongo
from multiprocessing import Process
import json
import time
import os
import requests
from bson.json_util import dumps
from app.encryption import manualDecrypt
from datetime import datetime

mainProc = None
allProcs = []
masterHandle = None
masterClient = None

def watchersInit(connStr, db, col):
    global mainProc
    global masterHandle
    global allProcs
    global masterClient
    
    allProcs = []

    print("INITIALIZING WATCHERS")
    masterClient = pymongo.MongoClient(connStr)
    masterHandle = masterClient[db][col]

    cursor = masterHandle.find({"enabled": True})

    for doc in cursor:
        proc = Process(target=runWatch, args=(doc["_id"], doc["connString"], doc["db"], doc["col"], json.loads(doc["pipeline"].replace("'","\"")), doc["resumeToken"], doc["webhook"], doc["secrets"]))
        proc.start()
        allProcs.append(proc)

    with masterHandle.watch([{'$match': {'operationType': {'$in':['update','delete']}, 'updateDescription.updatedFields.resumeToken':{'$exists':False}}}]) as stream:
        # any changes, restart
        for change in stream:
            print("MASTER CHANGE")
            print(change)
            for p in allProcs:
                print("Terminating process")
                os.kill(p.pid, 9)
            stream.close()

    watchersInit(connStr, db, col)
        

def runWatch(id, conStr, db, col, pipeline, rt, wh, secrets=None):
    global masterHandle
    global masterClient
    try:
        print ("Starting changestream thread against " +db + "." + col)
        resume_token = None
        
        client = pymongo.MongoClient(manualDecrypt(masterClient, conStr))
        handle = client[db][col]
        with handle.watch(pipeline, full_document="updateLookup") as stream:
            for change in stream:
                resume_token = stream.resume_token
                #print("SUBSCRIBER CHANGE")
                #print(change)
                change["secretsMetadata"] = secrets
                response = requests.post(wh, json=json.loads(dumps(change)))
                responseToInsert = ""

                try:
                    responseToInsert = json.loads(response.text)
                except:
                    responseToInsert = response.text
                    
                #print(response.text)
                masterHandle.update_one({"_id":id}, {"$set": {"resumeToken": resume_token, "webhookResponse": responseToInsert, "lastRan": datetime.utcnow() }})
                #print("resume token updated")
    except pymongo.errors.PyMongoError:
        print("Error in watcher")