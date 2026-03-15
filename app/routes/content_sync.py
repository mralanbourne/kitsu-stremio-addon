import json
import requests
from quart import Blueprint, Response
from app.services.db import get_valid_user

content_sync_bp = Blueprint("content_sync", __name__)
KITSU_API_URL = "https://kitsu.io/api/edge"

def get_kitsu_headers(access_token: str):
    return {
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
        "Authorization": f"Bearer {access_token}"
    }

@content_sync_bp.route("/<auth_id>/subtitles/<catalog_type>/<stremio_id>.json")
@content_sync_bp.route("/<auth_id>/subtitles/<catalog_type>/<stremio_id>/<path:extra>.json")
async def sync_progress(auth_id: str, catalog_type: str, stremio_id: str, extra: str = ""):
    print(f"--- SYNC REQUEST: id={stremio_id} ---")
    
    vtt_content = "WEBVTT\n\n00:00:00.000 --> 00:00:04.000\nKitsu: Sync sent"
    dummy_sub = {
        "subtitles": [{
            "id": "kitsu-sync-status",
            "url": f"data:text/vtt;charset=utf-8,{vtt_content}",
            "lang": "Kitsu Sync Info"
        }]
    }

    if not stremio_id.startswith("kitsu:"):
        return Response(json.dumps(dummy_sub), mimetype="application/json")

    parts = stremio_id.split(":")
    if len(parts) < 2:
        return Response(json.dumps(dummy_sub), mimetype="application/json")

    anime_id = parts[1]
    episode = 1  # Fallback for movies

    if len(parts) >= 4:
        try: episode = int(parts[3])
        except ValueError: pass
    elif len(parts) == 3:
        try: episode = int(parts[2])
        except ValueError: pass

    user, error = get_valid_user(auth_id)
    if error or not user:
        return Response(json.dumps(dummy_sub), mimetype="application/json")

    access_token = user.get("access_token")
    kitsu_user_id = user.get("id")
    headers = get_kitsu_headers(access_token)

    try:
        # 1. How many episodes does this anime have in total?
        anime_url = f"{KITSU_API_URL}/anime/{anime_id}"
        anime_resp = requests.get(anime_url, headers=headers)
        total_episodes = None
        if anime_resp.ok:
            total_episodes = anime_resp.json().get("data", {}).get("attributes", {}).get("episodeCount")
        
        # 2. Calculate the status
        target_status = "current" # Default to "Watching"
        if total_episodes and episode >= total_episodes:
            target_status = "completed" # Finale reached

        # 3. Check if the anime is already on the user's Kitsu list
        search_url = f"{KITSU_API_URL}/library-entries?filter[user_id]={kitsu_user_id}&filter[anime_id]={anime_id}"
        search_resp = requests.get(search_url, headers=headers)
        search_resp.raise_for_status()
        entries = search_resp.json().get("data", [])

        if entries:
            entry_id = entries[0]["id"]
            current_progress = entries[0]["attributes"].get("progress", 0)
            current_status = entries[0]["attributes"].get("status")

            # Update is only fired if the episode is higher OR was completed
            if episode > current_progress or (target_status == "completed" and current_status != "completed"):
                payload = {
                    "data": {
                        "id": entry_id,
                        "type": "libraryEntries",
                        "attributes": {
                            "progress": max(episode, current_progress),
                            "status": target_status
                        }
                    }
                }
                update_url = f"{KITSU_API_URL}/library-entries/{entry_id}"
                up_res = requests.patch(update_url, headers=headers, json=payload)
                if not up_res.ok:
                    print(f"Kitsu Update Error: {up_res.text}")
                else:
                    print(f"Kitsu Update: Anime {anime_id} -> Episode {episode} | Status: {target_status}")
        else:
            # Anime is new, we create it directly with the correct episode
            payload = {
                "data": {
                    "type": "libraryEntries",
                    "attributes": {
                        "progress": episode,
                        "status": target_status
                    },
                    "relationships": {
                        "user": {"data": { "type": "users", "id": str(kitsu_user_id) }},
                        "media": {"data": { "type": "anime", "id": str(anime_id) }}
                    }
                }
            }
            create_url = f"{KITSU_API_URL}/library-entries"
            cr_res = requests.post(create_url, headers=headers, json=payload)
            if not cr_res.ok:
                print(f"Kitsu Create Error: {cr_res.text}")
            else:
                print(f"Kitsu New: Anime {anime_id} -> Episode {episode} | Status: {target_status}")

    except Exception as e:
        print(f"Fatal error during sync: {e}")

    return Response(json.dumps(dummy_sub), mimetype="application/json")
