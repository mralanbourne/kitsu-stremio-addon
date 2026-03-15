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
    user_data = UID_map_collection.find_one({"uid": user_id})
    if user_data:
        return user_data
    return None

def store_user(user_details: dict) -> bool:
    user_id = user_details["id"]
    user_details["uid"] = user_id
    data = user_details.copy()

    if user := UID_map_collection.find_one({"uid": user_id}):
        return UID_map_collection.update_one({"_id": user["_id"]}, {"$set": data}).acknowledged
    return UID_map_collection.insert_one(data).acknowledged

def get_valid_user(user_id: str) -> tuple[dict, Optional[str]]:
    user = get_user(user_id)
    if not user:
        return {}, "No user found. Please re-login to Kitsu."

    if (
        not user.get("last_updated")
        or not user.get("expires_in")
        or not user.get("access_token")
        or not user.get("refresh_token")
    ):
        return {}, "Invalid Kitsu session. Please log in again."

    expiration_date = user["last_updated"] + timedelta(seconds=user["expires_in"])
    if datetime.utcnow() > expiration_date:
        return {}, "Kitsu session expired. Please refresh token or log in again."
        
    return user, None