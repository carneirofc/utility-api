from flask import escape, request, json
from application import app

from application.ldap.auth import Auth
from application.utils import get_logger


basic_headers = {
    "WWW-Authenticate": "Basic",
    "Cache-Control": "no-store",
    "Set-Cookie": "valid=yes; Max-Age=10; HttpOnly",
}


@app.route("/ldap/Archiver")
def auth():
    logger = get_logger()

    logger.debug("Headers: {}".format(request.headers))
    logger.debug("Cookies: {}".format(request.cookies))

    # Check if the auth has expired
    if "valid" not in request.cookies:
        logger.warn("Authorization expired!")
        return f"Authorization expired", 401, basic_headers

    auth = Auth(request.headers)

    if not auth.authenticate():
        logger.warn("Access denied!")
        return f"Access denied!", 401, basic_headers

    return f"Authorized!", 200
