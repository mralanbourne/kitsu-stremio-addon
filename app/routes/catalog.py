import requests
from quart import Blueprint, abort
from config import Config
from ..services.db import get_valid_user
from .manifest import MANIFEST
from .utils import respond_with

catalog_bp = Blueprint("catalog", __name__)
KITSU_API_URL = "https://kitsu.io/api/edge"

def _parse_stremio_filters(extra: str | None) -> dict:
    if not extra: return {}
    return {part.split("=")[0]: part.split("=")[1] for part in extra.split("&") if "=" in part}

@catalog_bp.route("/<user_id>/catalog/<string:catalog_type>/<string:catalog_id>.json", defaults={"extras": ""})
@catalog_bp.route("/<user_id>/catalog/<string:catalog_type>/<string:catalog_id>/<path:extras>.json")
async def addon_catalog(user_id: str, catalog_type: str, catalog_id: str, extras: str):
    valid_ids = [c["id"] for c in MANIFEST["catalogs"]]
    if catalog_type != "anime" or catalog_id not in valid_ids:
        abort(404)

    user, error = get_valid_user(user_id)
    if error:
        print(f"Catalog Error: User auth failed for {user_id} - {error}")
        return await respond_with({"metas": []}, stremio_response=True)

    filters = _parse_stremio_filters(extras)
    offset = int(filters.get("skip", 0))

    headers = {
        "Accept": "application/vnd.api+json",
        "Authorization": f"Bearer {user.get('access_token')}"
    }

    url = f"{KITSU_API_URL}/library-entries?filter[user_id]={user_id}&filter[kind]=anime&filter[status]={catalog_id}&include=anime&page[limit]=20&page[offset]={offset}&sort=-updatedAt"

    try:
        print(f"Querying Kitsu API: {url}")
        resp = requests.get(url, headers=headers, timeout=10)
        if not resp.ok:
            print(f"Kitsu API Error: {resp.text}")
            resp.raise_for_status()
            
        data = resp.json()

        entries = data.get("data", [])
        included = data.get("included", [])
        print(f"Success! Kitsu found {len(entries)} anime(s).")

        anime_dict = {}
        for item in included:
            if item.get("type") == "anime":
                anime_dict[item["id"]] = item.get("attributes", {})

        stremio_metas = []
        for entry in entries:
            try:
                anime_data = entry.get("relationships", {}).get("anime", {}).get("data")
                if not anime_data:
                    continue
                    
                anime_id = anime_data.get("id")
                anime_attrs = anime_dict.get(anime_id)

                if not anime_attrs:
                    continue

                title = anime_attrs.get("canonicalTitle")
                if not title:
                    title = anime_attrs.get("titles", {}).get("en_jp", "Unknown")
                    
                poster_img = anime_attrs.get("posterImage")
                poster = poster_img.get("large") if isinstance(poster_img, dict) else ""

                description = anime_attrs.get("synopsis") or ""

                stremio_metas.append({
                    "id": f"kitsu:{anime_id}",
                    "type": "anime",
                    "name": title,
                    "poster": poster,
                    "description": description
                })
            except Exception as item_ex:
                print(f"Error skipping anime entry: {item_ex}")
                continue

        print(f"Sending {len(stremio_metas)} titles to Stremio.")
        return await respond_with(
            {"metas": stremio_metas},
            private=True,
            cache_max_age=Config.CATALOG_ON_SUCCESS_DURATION,
            stale_revalidate=Config.CATALOG_STALE_WHILE_REVALIDATE,
            stremio_response=True
        )

    except Exception as e:
        print(f"Fatal error loading Kitsu catalog: {e}")
        return await respond_with({"metas": []}, stremio_response=True)