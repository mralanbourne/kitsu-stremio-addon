import certifi
from datetime import datetime, timedelta
from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from config import Config

client: MongoClient = MongoClient(Config.MONGO_URI, tlsCAFile=certifi.where())
db: Database = client.get_database(Config.MONGO_DB)
UID_map_collection: Collection = db.get_collection(Config.MONGO_UID_MAP)

def get_user(user_id: str) -> Optional[dict]:
    return UID_map_collection.find_one(
        {"uid": user_id}, 
        {
            "_id": 0, 
            "uid": 1,            
            "access_token": 1, 
            "id": 1, 
            "last_updated": 1, 
            "expires_in": 1, 
            "refresh_token": 1, 
            "progress": 1,
            "catalogs": 1         
        }
    )

def store_user(user_details: dict) -> bool:
    user_id = user_details["id"]
    user_details["uid"] = user_id
    data = user_details.copy()
    
    if user := UID_map_collection.find_one({"uid": user_id}, {"_id": 1}):
        return UID_map_collection.update_one({"_id": user["_id"]}, {"$set": data}).acknowledged
    return UID_map_collection.insert_one(data).acknowledged

def update_user_progress(user_id: str, anime_id: str, episode: int):
    UID_map_collection.update_one(
        {"uid": user_id},
        {"$set": {f"progress.{anime_id}": episode}}
    )

def get_valid_user(user_id: str) -> tuple[dict, Optional[str]]:
    user = get_user(user_id)
    if not user:
        return {}, "No user found. Please re-login to Kitsu."
        
    if not all(user.get(k) for k in ["last_updated", "expires_in", "access_token", "refresh_token"]):
        return {}, "Invalid Kitsu session. Please log in again."

    expiration_date = user["last_updated"] + timedelta(seconds=user["expires_in"])
    if datetime.utcnow() > expiration_date:
        return {}, "Kitsu session expired. Please refresh token or log in again."
    return user, None
