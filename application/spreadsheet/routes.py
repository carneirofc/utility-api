from flask import Blueprint, jsonify, request
from siriuscommon import get_logger

from ..exceptions import _stracktrace
from ..status import HttpStatusCode
from .client import BackendClient
from .common import InvalidCommand, InvalidDevice

# Set up a Blueprint
spreadsheet_bp = Blueprint(
    "spreadsheet_bp", __name__, template_folder="templates", static_folder="static"
)


logger = get_logger("Spreadsheet Routes")


@spreadsheet_bp.errorhandler(InvalidCommand)
def invalid_command(e):
    logger.exception("Invalid Command")
    return jsonify(e.to_dict()), e.status_code


@spreadsheet_bp.errorhandler(InvalidDevice)
def invalid_device(e):
    # logger.exception("Invalid Device")

    return jsonify(e.to_dict()), e.status_code


@spreadsheet_bp.errorhandler(Exception)
def internal_server_error(e):
    logger.exception("Unhandled exception")
    return (
        jsonify(message=str(e), stacktrace=_stracktrace()),
        HttpStatusCode.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@spreadsheet_bp.route("/reload")
def reload():
    client = BackendClient()
    client.reloadData()
    return "Data reloaded succesfully!", 200


@spreadsheet_bp.route("/status")
def status():
    # @todo: Return status information.
    return "Healthy!", 200


@spreadsheet_bp.route("/devices")
def devices():
    deviceType = request.args.get("type", None)
    ip = request.args.get("ip", None)

    client = BackendClient()
    response = client.getDevice(deviceType=deviceType, ip=ip)
    return response, 200
