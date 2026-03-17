from datetime import datetime
import httpx
from quart import Blueprint, flash, request, session, url_for, jsonify
from werkzeug.utils import redirect
from app.services.db import store_user

auth_blueprint = Blueprint("auth", __name__)

KITSU_OAUTH_URL = "https://kitsu.io/api/oauth/token"
KITSU_API_URL = "https://kitsu.io/api/edge"

KITSU_CLIENT_ID = "dd031b32d2f56c990b1425efe6c42ad847e7fe3ab46bf1299f05ecd856bdb7dd"
KITSU_CLIENT_SECRET = "54d7307928f63414defd96399fc31ba847961ceaecef3a5fd93144e960c0e151"

def _store_user_session(user_details: dict):
    session["user"] = user_details
    session.permanent = True

@auth_blueprint.route("/login", methods=["POST"])
async def login():
    if "user" in session:
        await flash("You are already logged in.", "warning")
        return redirect(url_for("ui.index"))

    form_data = await request.form
    username = form_data.get("username")
    password = form_data.get("password")

    if not username or not password:
        await flash("Email and password are required.", "danger")
        return redirect(url_for("ui.index"))

    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": KITSU_CLIENT_ID,
        "client_secret": KITSU_CLIENT_SECRET
    }

    try:
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(KITSU_OAUTH_URL, json=payload)
            
            if token_resp.status_code != 200:
                print(f"Kitsu Auth Error: {token_resp.text}")
                token_resp.raise_for_status()

            tokens = token_resp.json()
            
            headers = {
                "Authorization": f"Bearer {tokens['access_token']}",
                "Accept": "application/vnd.api+json"
            }
            user_resp = await client.get(f"{KITSU_API_URL}/users?filter[self]=true", headers=headers)
            
            if user_resp.status_code != 200:
                print(f"Kitsu User Error: {user_resp.text}")
                user_resp.raise_for_status()
            
            user_data = user_resp.json().get("data", [])
            if not user_data:
                print("Kitsu returned an empty user array.")
                raise ValueError("Could not load user profile from Kitsu.")
                
            kitsu_user_id = user_data[0]["id"]

            user_details = {
                "id": kitsu_user_id, 
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "expires_in": tokens["expires_in"],
                "last_updated": datetime.utcnow(),
            }

            await store_user(user_details)
            _store_user_session({"uid": kitsu_user_id, "refresh_token": tokens["refresh_token"]})
            await flash("Successfully logged into Kitsu!", "success")
            return redirect(url_for("ui.index"))

    except Exception as e:
        print(f"Login Exception: {e}")
        await flash("Login failed. Please check your credentials.", "danger")
        return redirect(url_for("ui.index"))

@auth_blueprint.route("/refresh")
async def refresh_token():
    user_session = session.get("user")
    if not user_session:
        return redirect(url_for("ui.index"))

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": user_session["refresh_token"],
        "client_id": KITSU_CLIENT_ID,
        "client_secret": KITSU_CLIENT_SECRET
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(KITSU_OAUTH_URL, json=payload)
            if resp.status_code != 200:
                print(f"Kitsu Refresh Error: {resp.text}")
                resp.raise_for_status()
                
            tokens = resp.json()

            user_details = {
                "id": user_session["uid"],
                "access_token": tokens["access_token"],
                "refresh_token": tokens.get("refresh_token", user_session["refresh_token"]),
                "expires_in": tokens["expires_in"],
                "last_updated": datetime.utcnow(),
            }

            await store_user(user_details)
            _store_user_session({"uid": user_session["uid"], "refresh_token": user_details["refresh_token"]})
            return redirect(url_for("ui.index"))

    except Exception as e:
        print(f"Refresh Exception: {e}")
        session.pop("user", None)
        await flash("Session expired. Please log in again.", "danger")
        return redirect(url_for("ui.index"))

@auth_blueprint.route("/logout")
async def logout():
    session.pop("user", None)
    return redirect(url_for("ui.index"))
