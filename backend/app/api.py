from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import pymongo
from bson.json_util import dumps
import json
from bson.objectid import ObjectId
import os
from app.watcher import watchersInit
from multiprocessing import Process
from multiprocessing import set_start_method
from datetime import datetime

set_start_method('fork', force=True)
sp = Process(target=watchersInit, args=(os.environ["SPECUIMDBCONNSTR"], "faas", "subscriptions"))
sp.start()
#threading.Thread(target=watchersInit, args=(os.environ["SPECUIMDBCONNSTR"], "faas", "subscriptions")).start()

class SubscriptionItem(BaseModel):
    name: str
    pipeline: str
    connString: str
    db: str
    col: str
    enabled: bool
    webhook: str

app = FastAPI(title="spa-app")
api_app = FastAPI(title="api-app")

app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

client = pymongo.MongoClient(os.environ["SPECUIMDBCONNSTR"])
db = client["faas"]
col = db["subscriptions"]

@api_app.get("/hello")
async def hello():
    return {"message": "Hello World"}
    
@api_app.get("/listAll")
async def listAll():
    cursor = col.find({})
    return json.loads(dumps(cursor))

@api_app.put("/save/{id}")
async def save(id:str, si: SubscriptionItem):
    datetime_now = datetime.utcnow()
    # i'm bad at python frameworks
    d = si.model_dump()
    d["modified"] = datetime_now
    col.update_one({"_id": ObjectId(id) }, {"$set": d })

@api_app.get("/delete/{id}")
async def delete(id:str):
    col.delete_one({"_id": ObjectId(id) })

@api_app.get("/new")
async def new():
    obj = {"name":"New Subscription", "pipeline":"[]", "connString":"", "db":"", "col":"", "enabled":False, "webhook":"", "modified":datetime.utcnow()}
    id = col.insert_one(obj).inserted_id
    obj["_id"] = id
    return json.loads(dumps(obj))