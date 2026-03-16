from quart import Blueprint, flash, make_response, redirect, render_template, request, session, url_for
from app.services.db import get_user, store_user

ui_bp = Blueprint("ui", __name__)

@ui_bp.route("/")
async def index():
    if session.get("user", None):
        return redirect(url_for("ui.configure"))
    response = await make_response(await render_template("index.html"))
    return response

@ui_bp.route("/configure", methods=["GET", "POST"])
@ui_bp.route("/<user_id>/configure")
async def configure(user_id: str = ""):
    if not (user_session := session.get("user")):
        return redirect(url_for("ui.index"))

    user = get_user(user_session["uid"])
    if not user:
        await flash("User not found. Please log in again.", "danger")
        return redirect(url_for("ui.index"))

    # Checken, ob der User das Addon zum ersten Mal konfiguriert
    is_new_user = user.get("catalogs") is None
    
    user_id = user["uid"]
    domain = request.host
    manifest_url = f"https://{domain}/{user_id}/manifest.json"
    manifest_magnet = f"stremio://{domain}/{user_id}/manifest.json"

    if request.method == "POST":
        form_data = await request.form
        user |= __handle_addon_options(form_data)
        if not store_user(user):
            await flash("Error saving configuration.", "danger")
            return redirect(url_for("ui.index"))

        if is_new_user:
            await flash("Settings saved! Now proceed to Step 2 below to install the addon.", "success")
        else:
            await flash("Settings updated! Stremio will sync your changes automatically within 60 seconds.", "success")
        
    return await make_response(
        await render_template(
            "configure.html",
            user=user,
            manifest_url=manifest_url,
            manifest_magnet=manifest_magnet,
        )
    )

def __handle_addon_options(addon_config_options):
    options = {"catalogs": []}
    if addon_config_options.get("include_planned"): options["catalogs"].append("planned")
    if addon_config_options.get("include_current"): options["catalogs"].append("current")
    if addon_config_options.get("include_completed"): options["catalogs"].append("completed")
    if addon_config_options.get("include_on_hold"): options["catalogs"].append("on_hold")
    if addon_config_options.get("include_dropped"): options["catalogs"].append("dropped")
    return options
