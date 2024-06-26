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

    # when we insert via NEW api call, its off so we dont need to watch insert
    # we need to check updates to see if the update was to turn something on/off
    # we need to check deletes to make sure we kill an on watcher
    # then since we persist the resume token and the webhook response and last ran time, we need to make sure we dont cause a recursive loop when we persist those
    # so don't restart if those are the fields that changed
    with masterHandle.watch([{'$match': {'operationType': {'$in':['update','delete']}, 'updateDescription.updatedFields.webhookResponse':{'$exists':False}, 'updateDescription.updatedFields.resumeToken':{'$exists':False}, 'updateDescription.updatedFields.lastRan':{'$exists':False} }}]) as stream:
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
        ra = None
        if "_data" in rt:
            ra = rt
        #print(ra)
        with handle.watch(pipeline, full_document="updateLookup", resume_after=ra) as stream:
            for change in stream:
                try:
                    resume_token = stream.resume_token
                    #print("SUBSCRIBER CHANGE")
                    #print(change)
                    change["secretsMetadata"] = secrets
                    response = requests.post(wh, json=json.loads(dumps(change)))
                    responseToInsert = parseRespose(response)
                    masterHandle.update_one({"_id":id}, {"$set": {"resumeToken": resume_token, "webhookResponse": responseToInsert, "lastRan": datetime.utcnow() }})
                    #print("resume token updated")
                except:
                    masterHandle.update_one({"_id":id}, {"$set": {"webhookResponse": "There was an error", "lastRan": datetime.utcnow() }})
    except pymongo.errors.PyMongoError as e:
        print("Error in watcher")
        print(e)

def parseRespose(response):
    responseToInsert = ""
    try:
        responseToInsert = json.loads(response.text)
    except:
        responseToInsert = response.text
    return responseToInsert