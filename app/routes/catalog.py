import requests
from urllib.parse import unquote
from quart import Blueprint, abort
from config import Config
from ..services.db import get_valid_user
from .manifest import MANIFEST
from .utils import respond_with

catalog_bp = Blueprint("catalog", __name__)
KITSU_API_URL = "https://kitsu.io/api/edge"

def _parse_stremio_filters(extra: str | None) -> dict:
    """Parses extra parameters from Stremio URL (skip, search, etc.)."""
    if not extra: return {}
    filters = {}
    for part in extra.split("&"):
        if "=" in part:
            k, v = part.split("=", 1)
            filters[k] = unquote(v)
    return filters

@catalog_bp.route("/<user_id>/catalog/<string:catalog_type>/<string:catalog_id>.json", defaults={"extras": ""})
@catalog_bp.route("/<user_id>/catalog/<string:catalog_type>/<string:catalog_id>/<path:extras>.json")
async def addon_catalog(user_id: str, catalog_type: str, catalog_id: str, extras: str):
    
    # Validate catalog ID against manifest
    valid_ids = [c["id"] for c in MANIFEST["catalogs"]]
    if catalog_type != "anime" or catalog_id not in valid_ids:
        abort(404)

    # Validate user session
    user, error = get_valid_user(user_id)
    if error:
        return await respond_with({"metas": []}, stremio_response=True)

    # START SMART CACHING LOGIC
    if catalog_id == "current":
        cache_time = 300
    elif catalog_id == "kitsu_search":
        cache_time = 0 
    else:
        cache_time = 300

    filters = _parse_stremio_filters(extras)
    headers = {
        "Accept": "application/vnd.api+json",
        "Authorization": f"Bearer {user.get('access_token')}"
    }

    stremio_metas = []

    try:
        # -----------------------------------------------------
        # LOGIC FOR THE SEARCH
        # -----------------------------------------------------
        if catalog_id == "kitsu_search":
            search_query = filters.get("search")
            if not search_query:
                return await respond_with({"metas": []}, stremio_response=True)
                
            url = f"{KITSU_API_URL}/anime?filter[text]={search_query}&page[limit]=20"
            resp = requests.get(url, headers=headers, timeout=5)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            
            for item in data:
                anime_id = item.get("id")
                attrs = item.get("attributes", {})
                
                title = attrs.get("canonicalTitle") or attrs.get("titles", {}).get("en_jp", "Unknown")
                poster_img = attrs.get("posterImage") or {}
                poster = poster_img.get("large") if isinstance(poster_img, dict) else ""
                description = attrs.get("synopsis") or ""

                stremio_metas.append({
                    "id": f"kitsu:{anime_id}",
                    "type": "anime",
                    "name": title,
                    "poster": poster,
                    "description": description
                })
        
        # -----------------------------------------------------
        # LOGIC FOR NORMAL LISTS (Watching, Planned etc.)
        # -----------------------------------------------------
        else:
            offset = int(filters.get("skip", 0))
            url = f"{KITSU_API_URL}/library-entries?filter[user_id]={user.get('id')}&filter[kind]=anime&filter[status]={catalog_id}&include=anime&page[limit]=20&page[offset]={offset}&sort=-updatedAt"

            resp = requests.get(url, headers=headers, timeout=5)
            resp.raise_for_status()
            
            data = resp.json()
            entries = data.get("data", [])
            included = data.get("included", [])

            # Create a dictionary for fast lookup of included anime attributes
            anime_dict = {item["id"]: item.get("attributes", {}) for item in included if item.get("type") == "anime"}

            for entry in entries:
                try:
                    anime_data = entry.get("relationships", {}).get("anime", {}).get("data")
                    if not anime_data: continue
                        
                    anime_id = anime_data.get("id")
                    anime_attrs = anime_dict.get(anime_id)
                    if not anime_attrs: continue

                    title = anime_attrs.get("canonicalTitle") or anime_attrs.get("titles", {}).get("en_jp", "Unknown")
                    poster_img = anime_attrs.get("posterImage") or {}
                    poster = poster_img.get("large") if isinstance(poster_img, dict) else ""
                    description = anime_attrs.get("synopsis") or ""

                    stremio_metas.append({
                        "id": f"kitsu:{anime_id}",
                        "type": "anime",
                        "name": title,
                        "poster": poster,
                        "description": description
                    })
                except Exception:
                    continue

        # Final response utilizing optimized caching headers
        return await respond_with(
            {"metas": stremio_metas},
            private=False,
            cache_max_age=cache_time,
            stale_revalidate=Config.DEFAULT_STALE_WHILE_REVALIDATE,
            stremio_response=True
        )

    except Exception as e:
        print(f"Catalog Error: {e}")
        return await respond_with({"metas": []}, stremio_response=True)
