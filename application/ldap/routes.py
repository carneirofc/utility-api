from flask import escape, request, json, Blueprint, current_app, make_response

from application.ldap.auth import Auth, generate_token, get_from_token
from application.utils import get_logger

import time


ldap_bp = Blueprint(
    "ldap_bp", __name__, template_folder="templates", static_folder="static"
)


@ldap_bp.route("/ldap/token/authorization", methods=["GET", "POST"])
def auth_token_authorization():
    """ Get the Authorization Basic from TOKEN """
    logger = get_logger()

    # Check if the auth has expired
    # Check if TOKEN
    #  Check if TOKEN is valid, return the authorization and add it to the request
    #  Signal that client should be disconnected?

    if "TOKEN" not in request.cookies:
        logger.warn("TOKEN not found in cookies.")
        return f"TOKEN not found", 401

    authorization = get_from_token(request.cookies["TOKEN"])
    return f"Authorized", 200, {"Authorization": authorization}


@ldap_bp.route("/ldap/token/generate", methods=["GET", "POST"])
def auth_token_generate():
    """ Generate a TOKEN cookie using LDAP and Basic Authorization """
    logger = get_logger()

    auth = Auth(request.headers)
    user, passw = auth.get_user_pass()

    if not auth.authenticate(user, passw):
        logger.warn("Access denied!")
        return f"Access denied!", 401

    token = generate_token(auth.authorization)
    response = make_response("Token generated", 200)
    response.set_cookie("TOKEN", token)

    return response


@ldap_bp.route("/ldap/Archiver")
def auth_archiver():
    logger = get_logger()

    logger.debug("Headers: {}".format(request.headers))
    logger.debug("Cookies: {}".format(request.cookies))

    basic_headers = {
        "WWW-Authenticate": "Basic",
        "Cache-Control": "no-store",
        "Set-Cookie": "valid=yes; Max-Age=10; HttpOnly",
    }

    # Check if the auth has expired
    if "valid" not in request.cookies:
        logger.warn("Authorization expired!")
        return f"Authorization expired", 401, basic_headers

    auth = Auth(request.headers)
    user, passw = auth.get_user_pass()

    if not auth.authenticate(user, passw):
        logger.warn("Access denied!")
        return f"Access denied!", 401, basic_headers

    return f"Authorized!", 200
