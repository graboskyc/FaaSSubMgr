import pymongo
from multiprocessing import Process
import json
import time
import os

mainProc = None
allProcs = []
masterHandle = None

def watchersInit(connStr, db, col):
    global mainProc
    global masterHandle
    global allProcs
    
    allProcs = []

    print("INITIALIZING WATCHERS")
    client = pymongo.MongoClient(connStr)
    masterHandle = client[db][col]

    cursor = masterHandle.find({"enabled": True})

    for doc in cursor:
        proc = Process(target=runWatch, args=(doc["_id"], doc["connString"], doc["db"], doc["col"], json.loads(doc["pipeline"].replace("'","\"")), doc["resumeToken"]))
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
        

def runWatch(id, conStr, db, col, pipeline, rt):
    global masterHandle
    try:
        print ("Starting changestream thread against " +db + "." + col)
        resume_token = None
        client = pymongo.MongoClient(conStr)
        handle = client[db][col]
        with handle.watch(pipeline) as stream:
            for change in stream:
                resume_token = stream.resume_token
                print(change)
                masterHandle.update_one({"_id":id}, {"$set": {"resumeToken": resume_token}})
    except pymongo.errors.PyMongoError:
        print("Error in watcher")