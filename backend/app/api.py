from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import pymongo
from bson.json_util import dumps
from bson.timestamp import Timestamp
from bson.objectid import ObjectId
import json
import os
from app.watcher import watchersInit
from multiprocessing import Process
from multiprocessing import set_start_method
from datetime import datetime
import requests
from app.encryption import initEncryption
from app.encryption import manualEncrypt
from app.encryption import manualDecrypt

initEncryption(os.environ["SPECUIMDBCONNSTR"].strip(), "faas", "whathappens")

set_start_method('fork', force=True)
sp = Process(target=watchersInit, args=(os.environ["SPECUIMDBCONNSTR"].strip(), "faas", "subscriptions"))
sp.start()

class SubscriptionItem(BaseModel):
    name: str
    pipeline: str
    connString: str
    db: str
    col: str
    enabled: bool
    webhook: str
    secrets: list

app = FastAPI(title="spa-app")
api_app = FastAPI(title="api-app")

app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

client = pymongo.MongoClient(os.environ["SPECUIMDBCONNSTR"].strip())
db = client["faas"]
col = db["subscriptions"]

@api_app.get("/hello")
async def hello():
    return {"message": "Hello World"}
    
@api_app.get("/listAll")
async def listAll():
    cursor = col.find({})
    return json.loads(dumps(cursor))

@api_app.get("/find/{id}")
async def save(id:str):
    # i'm bad at python frameworks
    d = col.find_one({"_id": ObjectId(id) })
    d["connString"] = manualDecrypt(client, d["connString"])
    decrArray = []
    for secret in d["secrets"]:
        decSecret = {}
        decSecret["key"] = secret["key"]
        decSecret["value"] = manualDecrypt(client, secret["value"])
        decrArray.append(decSecret)
    d["secrets"] = decrArray
    return json.loads(dumps(d))

@api_app.put("/save/{id}")
async def save(id:str, si: SubscriptionItem):
    datetime_now = datetime.utcnow()
    # i'm bad at python frameworks
    d = si.model_dump()
    d["modified"] = datetime_now
    d["connString"] = manualEncrypt(client, d["connString"])
    encrArray = []
    for secret in d["secrets"]:
        encSecret = {}
        encSecret["key"] = secret["key"]
        encSecret["value"] = manualEncrypt(client, secret["value"])
        encrArray.append(encSecret)
    d["secrets"] = encrArray
    col.update_one({"_id": ObjectId(id) }, {"$set": d })

@api_app.get("/delete/{id}")
async def delete(id:str):
    col.delete_one({"_id": ObjectId(id) })

@api_app.get("/new")
async def new():
    obj = {"name":"New Subscription", "pipeline":"[]", "connString":"mongodb+srv://...", "db":"", "col":"", "enabled":False, "webhook":"", "resumeToken":"", "modified":datetime.utcnow(), "secrets":[] }
    obj["connString"] = manualEncrypt(client, obj["connString"])
    id = col.insert_one(obj).inserted_id
    obj["_id"] = id
    obj["connString"] = manualDecrypt(client, obj["connString"])
    return json.loads(dumps(obj))

@api_app.post("/webhooktest/{id}")
async def save(id:str, si: SubscriptionItem):
    datetime_now = datetime.utcnow()
    # i'm bad at python frameworks
    d = si.model_dump()
    localclient = pymongo.MongoClient(d["connString"])
    localhandle = localclient[d["db"]][d["col"]]
    sampleDoc = localhandle.find_one({})

    retDoc = {
        '_id': {'_data': 'RESUMETOKEN'}, 
        'operationType': 'insert', 
        'clusterTime': Timestamp(1718150638, 1), 
        'wallTime': datetime(2024, 6, 12, 0, 3, 58, 343000), 
        'ns': {'db': 'news-demo', 'coll': 'test'}, 
        'documentKey': {'_id': ObjectId('6668e5deeb03e365f973122b')}
    }

    retDoc["fullDocument"] = sampleDoc
    retDoc["secretsMetadata"] = [{"HereIsOneSampleKey":"HereIsOneSampleValue"}]

    response = requests.post(d["webhook"], json=json.loads(dumps(retDoc)))
    return response.text

@api_app.put("/restart")
async def restart():
    datetime_now = datetime.utcnow()
    col.update_many({}, {"$set": {"poked":datetime_now} })