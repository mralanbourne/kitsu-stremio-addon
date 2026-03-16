import hashlib
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

    if request.method == "POST":
        form_data = await request.form
        user |= __handle_addon_options(form_data)
        if not store_user(user):
            await flash("Error saving configuration.", "danger")
            return redirect(url_for("ui.index"))

        await flash("Configuration saved! IMPORTANT: To apply these layout changes, you must uninstall the old addon in Stremio and install the new link below.", "success")

    # Hash-Generierung: Die URL ändert sich NUR, wenn Haken verändert werden.
    cats = user.get("catalogs", [])
    if not cats:
        config_hash = "new"
    else:
        config_hash = hashlib.md5("".join(sorted(cats)).encode()).hexdigest()[:8]
        
    user_id = user["uid"]
    domain = request.host
    manifest_url = f"https://{domain}/{user_id}/manifest.json?v={config_hash}"
    manifest_magnet = f"stremio://{domain}/{user_id}/manifest.json?v={config_hash}"

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
