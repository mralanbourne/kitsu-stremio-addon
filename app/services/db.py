import json
from datetime import datetime, timedelta
from typing import Optional
import httpx
from config import Config


headers = {"Authorization": f"Bearer {Config.UPSTASH_REDIS_REST_TOKEN}"}

async def _redis_request(method: str, endpoint: str, payload: str = None):

    async with httpx.AsyncClient() as client:
        url = f"{Config.UPSTASH_REDIS_REST_URL}/{endpoint}"
        
        try:
            if method == "GET":
                resp = await client.get(url, headers=headers)
            else:
           
                resp = await client.post(url, headers=headers, content=payload)
                
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            print(f"Upstash API Error: {e.response.text}")
            return {}

async def get_user(user_id: str) -> Optional[dict]:
    res = await _redis_request("GET", f"get/user:{user_id}")
    data = res.get("result")

    if not data:
        return None
        
    try:
        user = json.loads(data)

        if "last_updated" in user and isinstance(user["last_updated"], str):
            user["last_updated"] = datetime.fromisoformat(user["last_updated"])
        return user
    except Exception as e:
        print(f"Fehler beim Parsen der User-Daten: {e}")
        return None

async def store_user(user_details: dict) -> bool:

    user_id = user_details.get("uid") or user_details.get("id")
    user_details["uid"] = user_id
    
    data_to_store = user_details.copy()
    

    if "last_updated" in data_to_store and isinstance(data_to_store["last_updated"], datetime):
         data_to_store["last_updated"] = data_to_store["last_updated"].isoformat()
    

    payload_string = json.dumps(data_to_store)
    
    res = await _redis_request("POST", f"set/user:{user_id}", payload=payload_string)
    return res.get("result") == "OK"

async def update_user_progress(user_id: str, anime_id: str, episode: int):

    user = await get_user(user_id)
    if user:
        if "progress" not in user:
            user["progress"] = {}
            
        user["progress"][str(anime_id)] = episode
        await store_user(user)

async def get_valid_user(user_id: str) -> tuple[dict, Optional[str]]:

    user = await get_user(user_id)
    if not user:
        return {}, "No user found. Please re-login to Kitsu."
        
    if not all(user.get(k) for k in ["last_updated", "expires_in", "access_token", "refresh_token"]):
        return {}, "Invalid Kitsu session. Please log in again."

    expiration_date = user["last_updated"] + timedelta(seconds=user["expires_in"])
    if datetime.utcnow() > expiration_date:
        return {}, "Kitsu session expired. Please refresh token or log in again."
        
    return user, None
