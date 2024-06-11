from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import pymongo
from bson.json_util import dumps
import json
from bson.objectid import ObjectId
import os

class SubscriptionItem(BaseModel):
    name: str
    pipeline: str 
    resumeToken: str
    connString: str
    db: str
    col: str

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
    col.update_one({"_id": ObjectId(id) }, {"$set": si.model_dump() })