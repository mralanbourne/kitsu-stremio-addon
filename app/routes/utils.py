import datetime
import logging

from quart import Response, flash, jsonify, redirect, request, url_for
from requests import HTTPError

async def handle_auth_error(err: HTTPError):
    if not err.response:
        await flash(
            "No valid response received from Kitsu. The service might be down, please try again later.",
            "danger",
        )
        log_error("INVALID_RESPONSE", str(err), "No valid response from Kitsu", 500)
        return redirect(url_for("ui.index"))

    code = err.response.status_code
    body = err.response.text.strip()

    try:
        response = err.response.json()
        error_label = response.get("error", "No error label in response").upper()
        message = response.get(
            "message", "Unknown error occurred when trying to access Kitsu"
        )
        hint = response.get("hint", "No hint field in response")
        await flash(message, "danger")
        log_error(error_label, message, hint, code)
    except ValueError:
        await flash("Invalid response received from Kitsu.", "danger")
        log_error("INVALID_JSON", "Empty or invalid JSON response from Kitsu", body, code)
    return redirect(url_for("ui.index"))

def handle_api_error(err: HTTPError):
    code = err.response.status_code
    response = err.response.json()
    error_label = response.get("error", "No error label in response").upper()
    message = response.get(
        "message", "Unknown error occurred when trying to access Kitsu"
    )
    hint = response.get("hint", "No hint field in response")
    log_error(error_label, message, hint, code)

def log_error(error_label: str, message: str, hint: str, code: int = 0):
    logging.error(
        "%s [%s]\n  MESSAGE: %s\n  HINT:    %s",
        error_label,
        code,
        message,
        hint,
    )

async def respond_with(
    data: dict,
    private: bool = False,
    cache_max_age: int = 0,
    stale_revalidate: int = 0,
    stale_error: int = 0,
    stremio_response: bool = False,
) -> Response:
    if stremio_response:
        data = _add_stremio_headers(data, cache_max_age, stale_revalidate, stale_error)

    resp = jsonify(data)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"

    if cache_max_age > 0:
        resp.content_type = "application/json; charset=utf-8"
        resp.vary = "Accept-Encoding"
        await resp.add_etag(True)
        await resp.make_conditional(request)

        expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=cache_max_age)
        resp.expires = expires
        resp.headers["Expires"] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

        cache_control = [
            "private" if private else "public",
            f"max-age={cache_max_age}",
            f"s-maxage={cache_max_age}" if not private else "",
            (
                f"stale-while-revalidate={stale_revalidate}"
                if stale_revalidate > 0
                else ""
            ),
            f"stale-if-error={stale_error}" if stale_error > 0 else "",
        ]
        resp.headers["Cache-Control"] = ", ".join(filter(None, cache_control))
    return resp

def _add_stremio_headers(
    data: dict, cache_max_age: int, stale_revalidate: int, stale_error: int
) -> dict:
    if cache_max_age > 0:
        data["cacheMaxAge"] = cache_max_age
        data["staleRevalidate"] = stale_revalidate
        data["staleError"] = stale_error
    return data