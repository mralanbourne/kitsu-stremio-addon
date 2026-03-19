from typing import Any
from quart import Blueprint
from config import Config
from app.services.db import get_user
from app.routes.utils import respond_with

manifest_blueprint = Blueprint("manifest", __name__)

# Wir lassen die Genres drin, damit der Code nicht crasht, 
# aber wir zeigen sie eigentlich nicht mehr sinnvoll an.
genres = ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror", "Mecha", "Music", "Mystery", "Psychological", "Romance", "Sci-Fi", "Slice of Life", "Sports", "Supernatural", "Thriller"]

MANIFEST: dict[str, Any] = {
    "id": "org.kitsu-stremio-sync", # ID bleibt gleich, damit Stremio weiß, welches Addon es ist
    "version": "2.0.1",
    "name": "⚠️ [OLD] Kitsu Tracker - SHUTDOWN APR 10",
    "description": "🛑 THIS VERSION IS DEPRECATED. Shuts down April 10th due to server limits. Please reinstall the new 'Kitsu Tracker (V3.0.0)' from the community list or visit: kitsutracker.koyeb.app",
    # Wir nehmen ein Warn-Icon als Logo, damit es in der Liste sofort abstößt
    "logo": "https://img.icons8.com/color/512/warning-shield.png",
    "types": ["anime", "series", "movie"],
    "catalogs": [
        {
            "type": "anime",
            "id": "current",
            "name": "⚠️ MOVE TO V2 (Currently Watching)",
            "extra": [{"name": "skip"}]
        },
        {
            "type": "anime",
            "id": "kitsu_search",
            "name": "⚠️ MOVE TO V2 (Search)",
            "extra": [{"name": "search", "isRequired": True}]
        }
    ],
    "behaviorHints": {
        "configurable": True,
        "configurationRequired": True # Wir zwingen sie quasi zum Dashboard-Klick
    },
    "resources": ["catalog", "subtitles"], 
    "idPrefixes": ["kitsu"]
}

@manifest_blueprint.route("/manifest.json", methods=["GET", "OPTIONS"])
async def addon_unconfigured_manifest():
    unconfigured_manifest = MANIFEST.copy()
    unconfigured_manifest["behaviorHints"] = {
        "configurable": True,
        "configurationRequired": True,
    }
    return await respond_with(
        unconfigured_manifest,
        cache_max_age=Config.MANIFEST_DURATION,
        stale_revalidate=Config.DEFAULT_STALE_WHILE_REVALIDATE,
        stremio_response=False, 
    )

@manifest_blueprint.route("/<user_id>/manifest.json", methods=["GET", "OPTIONS"])
async def addon_configured_manifest(user_id: str):
    # Wir validieren den User zwar noch, aber wir geben ihm nur noch 
    # ein verstümmeltes Manifest zurück.
    user = await get_user(user_id)
    if not user:
        return await respond_with({"error": "User not found"}, private=True, cache_max_age=1800)
    
    user_manifest = MANIFEST.copy()
    # Wir ignorieren die User-Präferenzen und zeigen jedem die Warn-Kataloge
    return await respond_with(
        user_manifest, 
        stremio_response=False,
        cache_max_age=Config.MANIFEST_DURATION, 
        stale_revalidate=Config.DEFAULT_STALE_WHILE_REVALIDATE
    )
