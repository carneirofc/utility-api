from flask import Blueprint, jsonify, request

from ..common.exceptions import make_error_message
from ..common.status import HttpStatusCode
from ..common.utils import get_logger
from .client import BackendClient
from .common import InvalidCommand, InvalidDevice

# Set up a Blueprint
spreadsheet_bp = Blueprint(
    "spreadsheet_bp", __name__, template_folder="templates", static_folder="static"
)


logger = get_logger("Spreadsheet Routes")


@spreadsheet_bp.errorhandler(InvalidCommand)
def invalid_command(_e):
    e: InvalidCommand = _e
    logger.exception("Invalid Command")
    return jsonify(e.to_dict()), e.status_code


@spreadsheet_bp.errorhandler(InvalidDevice)
def invalid_device(_e):
    e: InvalidDevice = _e
    logger.exception("Invalid Device")
    return jsonify(e.to_dict()), e.status_code


@spreadsheet_bp.errorhandler(Exception)
def internal_server_error(e):
    logger.exception(f"Unhandled exception {e}")
    api_error = make_error_message(e)
    return jsonify(api_error), api_error.status_code


@spreadsheet_bp.route("/reload")
def reload():
    client = BackendClient()
    client.reloadData()
    return "Data reloaded succesfully!", HttpStatusCode.HTTP_200_OK


@spreadsheet_bp.route("/status")
def status():
    # @todo: Return status information.
    return "Healthy!", HttpStatusCode.HTTP_200_OK


@spreadsheet_bp.route("/devices")
def devices():
    deviceType = request.args.get("type", None)
    ip = request.args.get("ip", None)

    client = BackendClient()
    response = client.getDevice(deviceType=deviceType, ip=ip)
    return response, HttpStatusCode.HTTP_200_OK
