from flask import Blueprint, request
from siriuscommon import get_logger
from siriuscommon.spreadsheet import SheetName

from .client import BackendClient, InvalidCommand, InvalidDevice

# Set up a Blueprint
spreadsheet_bp = Blueprint(
    "spreadsheet_bp", __name__, template_folder="templates", static_folder="static"
)


logger = get_logger("Spreadsheet Routes")


@spreadsheet_bp.route("/reload")
def reload():
    try:
        client = BackendClient()
        client.reloadData()
        return "Data reloaded succesfully!", 200

    except Exception:
        logger.exception("reload entries failed.")
        return (
            "Unable to update entries from spreadsheet.",
            400,
        )


@spreadsheet_bp.route("/status")
def status():
    # @todo: Return status information.
    return "Healthy!", 200


@spreadsheet_bp.route("/devices")
def devices():
    deviceType = request.args.get("type", None)
    ip = request.args.get("ip", None)

    try:
        client = BackendClient()
        response = client.getDevice(deviceType=deviceType, ip=ip)
        return response, 200

    except (InvalidDevice, InvalidCommand) as e:
        logger.error("{}".format(e))
    except Exception:
        logger.exception("Internal exception")

    return (
        'Invalid response from backend. Available "deviceType" options are "{}".'.format(
            SheetName.keys()
        ),
        422,
    )
